from typing import Any, Dict
from pathlib import Path

import torch

from helm.common.cache import CacheConfig
from helm.common.optional_dependencies import handle_module_not_found_error
from .caching_tokenizer import CachingTokenizer

try:
    from lit_gpt import Tokenizer as InternalTokenizer
    from lit_gpt.utils import check_valid_checkpoint_dir
except ModuleNotFoundError as e:
    handle_module_not_found_error(e)


class LitGPTTokenizer(CachingTokenizer):
    def __init__(self, cache_config: CacheConfig, checkpoint_dir: Path = Path(""), device: str = "auto") -> None:
        super().__init__(cache_config)
        check_valid_checkpoint_dir(checkpoint_dir)
        self._tokenizer = InternalTokenizer(checkpoint_dir)
        self._device = device

    def _tokenize_do_it(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # TODO: This does not support encoding
        encoded = self._tokenizer.encode(request["text"], bos=True, eos=False, device=self._device)
        tokens = encoded.tolist()
        if not request["encode"]:
            return {"token_strings": tokens}
        return {"token_ids": tokens}

    def _decode_do_it(self, request: Dict[str, Any]) -> Dict[str, Any]:
        text = self._tokenizer.decode(torch.as_tensor(request["tokens"], dtype=torch.int))
        return {"text": text}
