# finish the export from RoboFog.

import os
import sys
import shutil
from fontParts.world import RFont


"""

    put the background glyphs in the right place
    clean up stray points

"""


def asDict(attribute):
    # stolen from RoboFab.
    d = {}
    for name in attribute.fontInfoAttributesVersion3:
        try:
            value = getattr(attribute, name)
        except AttributeError:
            # print("%s attribute not supported"%name)
            continue
        if value:
            d[name] = getattr(attribute, name)
    return d


def cleanupBackground(f):
    moved = []
    # background glyphs that have contours
    background_glyphs = [g.name for g in f if g.name[0] == '#' and len(g.contours)]
    foreground_glyphs = [gname.replace("#", "") for gname in background_glyphs]
    for glyph_name in foreground_glyphs:
        if glyph_name not in f.keys():
            f.newGlyph(glyph_name)
            print("creating new empty foreground glyph %s" % glyph_name)

    # XXX compare if foreground glyph is equal to background glyph and do
    # not write if that is the case

    # XXX create referenced component glyphs that do no longer exist (?)
    for g in f:
        if g.name[0] == "#":
            # do we have a foreground companion?
            other = g.name.replace("#", "")
            if other not in f:
                if len(g.contours):
                    print("background glyph %s has no foreground" % g.name)
                continue
            g_other = f[other]
            moved.append(g.name)
            if not g_other.contours == g.contours:
                bg = g_other.newLayer("background")
                bg.clear()
                bg.appendGlyph(g)
            else:
                print(
                    'background contours same as foreground contours, '
                    f'skipping {g.name}')
    for name in moved:
        f.removeGlyph(name)


input_folder = os.path.normpath(sys.argv[-1])
space_glyphs = ['space', 'nbspace']
ufo_files = []
for root, folders, files in os.walk(input_folder):
    ufos = [f for f in folders if f.endswith('.ufo')]
    if ufos:
        ufo_files.extend([os.path.join(root, ufo) for ufo in ufos])

for ufo_path in sorted(ufo_files):
    directory, file_name = os.path.split(ufo_path)
    file_stem, file_suffix = os.path.splitext(file_name)
    underline = '*' * len(file_stem)
    print(f'{file_stem}\n{underline}')
    new_ufo_name = f'{file_stem}_UFO3{file_suffix}'
    new_ufo_path = os.path.join(directory, new_ufo_name)
    old_f = RFont(ufo_path)
    new_f = RFont()

    for key, value in asDict(old_f.info).items():
        setattr(new_f.info, key, value)
    for glyphname in sorted(old_f.keys()):
        glyph = old_f[glyphname]

        # some RoboFog glyphs have only a stray point.
        # not an anchor, I assume.
        if(
            len(glyph.contours) == 1 and
            len(glyph.contours[0]) == 1 and
            glyph.name not in space_glyphs
        ):
            continue
        else:
            new_f.insertGlyph(glyph)
            new_glyph = new_f[glyphname]
            # space glyphs may still make it over and need to be cleared.
            if len(glyph.contours) == 1 and len(glyph.contours[0]) == 1:
                # print(f'clearing stray point in {glyphname}')
                new_glyph.clear()

    new_f.newLayer('background')
    cleanupBackground(new_f)
    glyph_order = list(old_f.glyphOrder[:256])
    for gname in old_f.glyphOrder[256:]:
        if gname in new_f.keys():
            glyph_order.append(gname)
    new_f.glyphOrder = glyph_order

    new_f.save(new_ufo_path)
    # old_f.close()
    shutil.rmtree(ufo_path)
    os.rename(new_ufo_path, ufo_path)
    print(f'done\n')

print('all done')
