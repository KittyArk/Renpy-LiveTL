# =============================================================================
# LiveTL —— 字体替换
#
# 汉化后原文的字体往往不含中文字形（显示成方块）。
# 这里用 Ren'Py 自带的 config.font_replacement_map，
# 把游戏里用到的字体统一映射到本插件自带的中文字体（MiSans）。
#
# 做法参考 KittyArk/Renpy_fonts_replacement（MIT 许可）。
#   原项目：https://github.com/KittyArk/Renpy_fonts_replacement
#   许可证：licenses/Renpy_fonts_replacement-LICENSE.txt
#
# MiSans 字体版权归小米科技所有，许可协议见 licenses/MiSans-LICENSE.pdf。
# =============================================================================

init -50 python:
    import os
    import re

    # 匹配脚本里出现的字体文件名，例如 "fonts/xxx.ttf"
    _livetl_font_pattern = re.compile(r'["\']([^"\']+\.(?:ttf|otf|ttc))["\']', re.IGNORECASE)

    def livetl_collect_fonts():
        """收集游戏里用到的字体文件名。

        扫描游戏脚本中出现过的 *.ttf / *.otf / *.ttc 字符串，
        和原项目里 extract_fonts.py 的思路一致。
        """
        fonts = set()

        if not livetl_scan_fonts:
            return []

        try:
            from renpy.translation import generation as gen
            filenames = gen.translate_list_files()
        except Exception:
            filenames = []

        for filename in filenames:
            try:
                with open(filename, "r", encoding="utf-8", errors="ignore") as f:
                    for m in _livetl_font_pattern.finditer(f.read()):
                        fonts.add(m.group(1))
            except Exception:
                pass

        return sorted(fonts)

    def livetl_apply_font_replacement():
        """把游戏用到的字体全部映射到指定的字体。"""
        if not livetl_replace_fonts or not livetl_font:
            return 0

        target_font = livetl_font

        # 字体文件不存在就跳过（不然游戏会因为找不到字体起不来）
        if not renpy.loadable(target_font):
            livetl_log("font replacement skipped: {!r} not found".format(target_font))
            return 0

        fonts = livetl_collect_fonts()

        count = 0

        for old_font in fonts:
            if old_font == target_font:
                continue

            # 常规 / 粗体 / 斜体 / 粗斜体 四种组合都要映射，
            # 统一直接替换为 livetl_font 指定字体。
            for is_bold in (False, True):
                for italic in (False, True):
                    config.font_replacement_map[old_font, is_bold, italic] = (target_font, is_bold, italic)

            count += 1

        livetl_log("font replacement: {} fonts -> {!r}".format(count, target_font))
        return count


init 100 python:

    # 脚本加载完成后执行一次替换
    livetl_apply_font_replacement()
