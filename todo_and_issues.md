# TODO
## MTGlyphPreview
- improve tracking whenever the glyph is incompatible

## master compatibility table (mct)

problem with updating the font/glyph– I'm assuming that masterprocessor is messing with glyph.changed updates, therefore it resets the table's cells highlightings

## kink manager

# ISSUES

### issue general #1: 
- layer functionality ?
```
Traceback (most recent call last):
  File "lib/eventTools/eventManager.pyc", line 131, in callObserver_withMethod_forEvent_withInfo_
  File "/Users/rafaelbuchner/Documents/+PRACA+/+GOOGLE+/master-tools/master-tools.roboFontExt/lib/masterTools/../masterTools/UI/vanillaSubClasses.py", line 83, in currentGlyphChangedCallback
  File "/Users/rafaelbuchner/Documents/+PRACA+/+GOOGLE+/master-tools/master-tools.roboFontExt/lib/masterTools/../masterTools/UI/vanillaSubClasses.py", line 211, in setGlyph
  File "/Users/rafaelbuchner/Documents/+PRACA+/+GOOGLE+/master-tools/master-tools.roboFontExt/lib/masterTools/../masterTools/UI/vanillaSubClasses.py", line 260, in _getInterpolation
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/ufoProcessor/__init__.py", line 440, in getGlyphMutator
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/ufoProcessor/__init__.py", line 487, in collectMastersForGlyph
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontParts/base/layer.py", line 170, in __contains__
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontParts/base/layer.py", line 184, in _contains
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontParts/base/layer.py", line 148, in keys
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontParts/base/font.py", line 1028, in _keys
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontParts/base/base.py", line 90, in __get__
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontParts/base/font.py", line 753, in _get_base_defaultLayer
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontParts/base/base.py", line 90, in __get__
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontParts/base/font.py", line 693, in _get_base_defaultLayerName
  File "/Applications/RoboFont.app/Contents/Resources/lib/python3.6/fontParts/fontshell/font.py", line 103, in _get_defaultLayerName
AttributeError: 'NoneType' object has no attribute 'layers'
```


Now I'm working on the highlighting in the MCT. I was able to get rid of the white gaps between the cells. Now I'm figuring out how to fix the issue, in which the highlighting resets. I realised that masterprocessor's font update can mess with that. Interesting thing: if I remove any point, number of ran glyph.changed callbacks is different than when I'm adding the point> Also take in the considaration that masterprocessor.font.update can mess with it.

DO WE NEED UPDATE FONTS connected with GLYPH.CHANGED?