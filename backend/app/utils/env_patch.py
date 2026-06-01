"""
Environment patches that must run before any transformers / torch import.
Fixes protobuf version conflicts in mixed Python environments (e.g. Windows
with TensorFlow also installed in user site-packages).
"""

import os
import sys

# Suppress TF log spam
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# Tell transformers to use ONLY PyTorch — do not attempt TF import at all
# (TensorFlow installed in this env has a broken protobuf dependency)
os.environ["USE_TF"] = "0"
os.environ["USE_JAX"] = "0"


def patch_protobuf():
    """
    Some protobuf installs (< 4.25 or user-level overrides) are missing
    `runtime_version`. Patch it in so transformers can import cleanly.
    """
    try:
        import google.protobuf as _pb
        if not hasattr(_pb, "runtime_version"):
            from types import SimpleNamespace
            # Minimal stub — only what transformers checks
            _pb.runtime_version = SimpleNamespace(
                OSS_RUNTIME=True,
                DOMAIN=None,
                MAJOR=4,
                MINOR=21,
                PATCH=12,
                SUFFIX="",
                VERSION_STRING="4.21.12",
                IS_PACKAGED_WITH_PROTOC=False,
            )
    except Exception:
        pass


patch_protobuf()
