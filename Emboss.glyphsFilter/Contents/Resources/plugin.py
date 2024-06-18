# encoding: utf-8

###########################################################################################################
#
#
#	Filter with dialog Plugin
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter%20with%20Dialog
#
#	For help on the use of Xcode:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#
###########################################################################################################

from __future__ import division, print_function, unicode_literals
import objc, math
from GlyphsApp import *
from GlyphsApp.plugins import *
from Foundation import NSClassFromString
from AppKit import NSAffineTransform, NSAffineTransformStruct


def calculateOffsetFromAngle(angle_degrees, distance):
	# Convert the angle from degrees to radians
	angle_radians = math.radians(angle_degrees)
	
	# Calculate the x and y offsets
	x_offset = round(distance * math.cos(angle_radians))
	y_offset = round(distance * math.sin(angle_radians))
	
	return x_offset, y_offset


def offsetLayer(thisLayer, offset, makeStroke=False, position=0.5, autoStroke=False):
	offsetFilter = NSClassFromString("GlyphsFilterOffsetCurve")
	offsetFilter.offsetLayer_offsetX_offsetY_makeStroke_autoStroke_position_metrics_error_shadow_capStyleStart_capStyleEnd_keepCompatibleOutlines_(
		thisLayer,
		offset, offset, # horizontal and vertical offset
		makeStroke,	    # if True, creates a stroke
		autoStroke,	    # if True, distorts resulting shape to vertical metrics
		position,	    # stroke distribution to the left and right, 0.5 = middle
		None, None, None, 0, 0, False)


def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct() # returns the 6-float tuple
	Apply the matrix tuple like this:
		Layer.applyTransform(tMatrix)
		Component.applyTransform(tMatrix)
		Path.applyTransform(tMatrix)
	Chain multiple NSAffineTransform objects t1, t2 like this:
		t1.appendTransform_(t2)
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX,shiftY)
	if skew:
		myTransform.shearXBy_(math.tan(math.radians(skew)))
	return myTransform


class Emboss(FilterWithDialog):

	# Definitions of IBOutlets

	# The NSView object from the User Interface. Keep this here!
	dialog = objc.IBOutlet()

	# Fields in dialog
	outerRimOffsetField = objc.IBOutlet()
	outerRimDistanceField = objc.IBOutlet()
	outerRimAngleField = objc.IBOutlet()
	innerOverlayOffsetField = objc.IBOutlet()
	innerOverlayAngleField = objc.IBOutlet()
	debrisThresholdField = objc.IBOutlet()

	@objc.python_method
	def settings(self):
		self.menuName = Glyphs.localize({
			'en': 'Emboss',
			# 'de': 'Mein Filter',
			# 'fr': 'Mon filtre',
			# 'es': 'Mi filtro',
			# 'pt': 'Meu filtro',
			# 'jp': '私のフィルター',
			# 'ko': '내 필터',
			# 'zh': '我的过滤器',
			})
		
		# Word on Run Button (default: Apply)
		self.actionButtonLabel = Glyphs.localize({
			'en': 'Emboss',
			# 'de': 'Anwenden',
			# 'fr': 'Appliquer',
			# 'es': 'Aplicar',
			# 'pt': 'Aplique',
			# 'jp': '申し込む',
			# 'ko': '대다',
			# 'zh': '应用',
			})
		
		# Load dialog from .nib (without .extension)
		self.loadNib('IBdialog', __file__)

	@objc.python_method
	def prefName(self, name):
		return f"com.mekkablue.emboss.{name.strip()}"

	@objc.python_method
	def pref(self, name):
		return Glyphs.defaults[self.prefName(name)]
	
	@objc.python_method
	def setPref(self, name, value):
		Glyphs.defaults[self.prefName(name)] = value
	
	# On dialog show
	@objc.python_method
	def start(self):
		
		# Set default value
		Glyphs.registerDefault(self.prefName('outerRimOffset'), 20.0)
		Glyphs.registerDefault(self.prefName('outerRimDistance'), 0.0)
		Glyphs.registerDefault(self.prefName('outerRimAngle'), 10.0)
		Glyphs.registerDefault(self.prefName('innerOverlayOffset'), 20.0)
		Glyphs.registerDefault(self.prefName('innerOverlayAngle'), 15.0)
		Glyphs.registerDefault(self.prefName('debrisThreshold'), 15.0)
		
		# Set value of text field
		self.outerRimOffsetField.setStringValue_(self.pref('outerRimOffset'))
		self.outerRimDistanceField.setStringValue_(self.pref('outerRimDistance'))
		self.outerRimAngleField.setStringValue_(self.pref('outerRimAngle'))
		self.innerOverlayOffsetField.setStringValue_(self.pref('innerOverlayOffset'))
		self.innerOverlayAngleField.setStringValue_(self.pref('innerOverlayAngle'))
		self.debrisThresholdField.setStringValue_(self.pref('debrisThreshold'))
		
		# Set focus to text field
		self.outerRimOffsetField.becomeFirstResponder()

	# Action triggered by UI
	@objc.IBAction
	def setOuterRimOffset_(self, sender):
		self.setPref('outerRimOffset', sender.floatValue())
		self.update()

	@objc.IBAction
	def setOuterRimDistance_(self, sender):
		self.setPref('outerRimDistance', sender.floatValue())
		self.update()

	@objc.IBAction
	def setOuterRimAngle_(self, sender):
		self.setPref('outerRimAngle', sender.floatValue())
		self.update()

	@objc.IBAction
	def setInnerOverlayOffset_(self, sender):
		self.setPref('innerOverlayOffset', sender.floatValue())
		self.update()

	@objc.IBAction
	def setInnerOverlayAngle_(self, sender):
		self.setPref('innerOverlayAngle', sender.floatValue())
		self.update()

	@objc.IBAction
	def setDebrisThreshold_(self, sender):
		self.setPref('debrisThreshold', sender.floatValue())
		self.update()

	# Actual filter
	@objc.python_method
	def filter(self, layer, inEditView, customParameters):
		
		# Called on font export, get value from customParameters
		if "outerRimOffset" in customParameters:
			outerRimOffset = customParameters["outerRimOffset"]
		else:
			outerRimOffset = float(self.pref("outerRimOffset"))
		
		if "outerRimDistance" in customParameters:
			outerRimDistance = customParameters["outerRimDistance"]
		else:
			outerRimDistance = float(self.pref("outerRimDistance"))
		
		if "outerRimAngle" in customParameters:
			outerRimAngle = customParameters["outerRimAngle"]
		else:
			outerRimAngle = float(self.pref("outerRimAngle"))
		
		if "innerOverlayOffset" in customParameters:
			innerOverlayOffset = customParameters["innerOverlayOffset"]
		else:
			innerOverlayOffset = float(self.pref("innerOverlayOffset"))
		
		if "innerOverlayAngle" in customParameters:
			innerOverlayAngle = customParameters["innerOverlayAngle"]
		else:
			innerOverlayAngle = float(self.pref("innerOverlayAngle"))
		
		if "debrisThreshold" in customParameters:
			debrisThreshold = customParameters["debrisThreshold"]
		else:
			debrisThreshold = float(self.pref("debrisThreshold"))
		
		
		outerRim = layer.copyDecomposedLayer()
		offsetLayer(outerRim, outerRimOffset)
		outerRim.removeOverlap()
		outerRim.correctPathDirection()
		if outerRimDistance != 0:
			x, y = calculateOffsetFromAngle(outerRimAngle, outerRimDistance)
			if x != 0 or y != 0:
				outerRim.applyTransform(
					transform(shiftX=x, shiftY=y).transformStruct()
					)
					
		if innerOverlayOffset != 0:
			subtractLayer = layer.copyDecomposedLayer()
			x, y = calculateOffsetFromAngle(innerOverlayAngle, innerOverlayOffset)
			subtractLayer.applyTransform(
				transform(shiftX=x, shiftY=y).transformStruct()
				)
				
			layer.pathSubtract_from_keepOverlaps_error_(
				list([p for p in subtractLayer.paths if isinstance(p, GSPath)]),
				list([p for p in layer.paths if isinstance(p, GSPath)]),
				False, None,
			)
		else:
			layer = layer.copyDecomposedLayer()
			layer.removeOverlap()
			layer.correctPathDirection()
			
		for path in layer.paths:
			path.reverse()
		
		for i, shape in enumerate(outerRim.shapes):
			layer.insertObject_inShapesAtIndex_(shape, i)
		
		for i in range(len(layer.shapes)-1, -1, -1):
			if layer.shapes[i].area() < debrisThreshold:
				del layer.shapes[i]

	@objc.python_method
	def generateCustomParameter(self):
		return "%s; outerRimOffset: %s, outerRimDistance: %s, outerRimAngle: %s, innerOverlayOffset: %s, innerOverlayAngle: %s, debrisThreshold: %s" % (
			self.__class__.__name__,
			self.pref("outerRimOffset"),
			self.pref("outerRimDistance"),
			self.pref("outerRimAngle"),
			self.pref("innerOverlayOffset"),
			self.pref("innerOverlayAngle"),
			self.pref("debrisThreshold"),
			)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
