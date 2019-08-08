# TODO
## MTGlyphPreview
- improve tracking whenever the glyph is incompatible

## master compatibility table (mct)

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