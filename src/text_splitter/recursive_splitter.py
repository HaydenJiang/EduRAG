from typing import List
from src.text_splitter.base_splitter import BaseTextSplitter

class RecursiveCharSplitter(BaseTextSplitter):
    # 分割优先级：先大分隔符，再小分隔符
    separators = ["\n\n", "\n", "。", "，", " ", ""]

    def split_text(self, text: str) -> List[str]:
        return self._recursive_split(text, self.separators)

    def _recursive_split(self, text: str, seps: List[str]) -> List[str]:
        # 当前层级无分隔符，直接按字符硬切
        if len(seps) == 1:
            return self._split_by_char(text, seps[0])

        sep = seps[0]
        # 按当前分隔符拆分
        chunks = text.split(sep)
        final_chunks = []
        good_chunks = []    # 缓存：长度小于阈值的短句，后续合并拼接

        for chunk in chunks:
            # 单段长度小于阈值，暂时缓存
            if len(chunk) < self.chunk_size:
                good_chunks.append(chunk)
                continue
            # 当前片段过长，递归用下一级更小分隔符拆分
            sub_chunks = self._recursive_split(chunk, seps[1:])
            final_chunks.extend(sub_chunks)

        # 合并缓存的短片段，带重叠窗口
        merged = self._merge_short_chunks(good_chunks, sep)
        final_chunks.extend(merged)
        return final_chunks

    def _split_by_char(self, text: str, sep: str) -> List[str]:
        """兜底：纯字符强制分割"""
        res = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            res.append(text[start:end])
            start += self.chunk_size - self.chunk_overlap
        return res

    def _merge_short_chunks(self, chunks: List[str], sep: str) -> List[str]:
        """合并小段文本，控制长度+重叠"""
        merged = []
        current = []
        current_len = 0

        for seg in chunks:
            seg_len = len(seg) + len(sep)
            # 加入后不超限则拼接
            if current_len + seg_len <= self.chunk_size:
                current.append(seg)
                current_len += seg_len
            else:
                # 保存当前块
                merged.append(sep.join(current))
                # 滑动窗口：保留末尾重叠部分
                overlap_count = max(0, len(current) - 2)
                current = current[overlap_count:]
                current_len = sum(len(s) + len(sep) for s in current)
                current.append(seg)
                current_len += seg_len
        # 加入最后剩余片段
        if current:
            merged.append(sep.join(current))
        return merged

# 全局默认分片器（块大小800，重叠150字符）
default_text_splitter = RecursiveCharSplitter(chunk_size=800, chunk_overlap=150)