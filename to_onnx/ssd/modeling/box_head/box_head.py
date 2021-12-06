from torch import nn, sigmoid
import torch.nn.functional as F

from .. import registry
from to_onnx.ssd.modeling.anchors.prior_box import PriorBox
from to_onnx.ssd.modeling.box_head.box_predictor import make_box_predictor
from to_onnx.ssd.utils import box_utils
from .inference import PostProcessor
from .loss import MultiBoxLoss


@registry.BOX_HEADS.register('SSDBoxHead')
class SSDBoxHead(nn.Module):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.use_sigmoid = cfg.MODEL.BOX_HEAD.USE_SIGMOID
        self.predictor = make_box_predictor(cfg)
        self.loss_evaluator = MultiBoxLoss(neg_pos_ratio=cfg.MODEL.NEG_POS_RATIO,
                                           use_sigmoid=self.use_sigmoid, focal_loss=cfg.MODEL.BOX_HEAD.FOCAL_LOSS)
        self.post_processor = PostProcessor(cfg)
        self.priors = None

    def forward(self, features, targets=None):
        cls_logits, bbox_pred = self.predictor(features)
        if self.training:
            return self._forward_train(cls_logits, bbox_pred, targets)
        else:
            return self._forward_test(cls_logits, bbox_pred)

    def _forward_train(self, cls_logits, bbox_pred, targets):
        gt_boxes, gt_labels = targets['boxes'], targets['labels']
        reg_loss, cls_loss = self.loss_evaluator(cls_logits, bbox_pred, gt_labels, gt_boxes)
        loss_dict = dict(
            reg_loss=reg_loss,
            cls_loss=cls_loss,
        )
        detections = (cls_logits, bbox_pred)
        return detections, loss_dict

    def _forward_test(self, cls_logits, bbox_pred):
        if self.priors is None:
            self.priors = PriorBox(self.cfg)().to(bbox_pred.device)
        scores = []
        if self.use_sigmoid:
            scores = sigmoid(cls_logits)
        else:
            scores = F.softmax(cls_logits, dim=2)
        boxes = box_utils.convert_locations_to_boxes(
            bbox_pred, self.priors, self.cfg.MODEL.CENTER_VARIANCE, self.cfg.MODEL.SIZE_VARIANCE
        )
        boxes = box_utils.center_form_to_corner_form(boxes)
        detections = (scores, boxes)
        detections = self.post_processor(detections)
        return detections, {}
