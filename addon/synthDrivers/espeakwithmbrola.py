# -*- coding: UTF-8 -*-
#synthDrivers/espeak.py
#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2007-2019 NV Access Limited, Peter Vágner, Aleksey Sadovoy, Leonard de Ruijter
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import os
from collections import OrderedDict
from . import _espeak_mb
import threading
import languageHandler
from synthDriverHandler import SynthDriver, VoiceInfo, synthIndexReached, synthDoneSpeaking
import speech
from logHandler import log

from speech.commands import (
	IndexCommand,
	CharacterModeCommand,
	LangChangeCommand,
	BreakCommand,
	PitchCommand,
	RateCommand,
	VolumeCommand,
	PhonemeCommand,
)

class SynthDriver(SynthDriver):
	name = "espeakwithmbrola"
	description = "espeak with mbrola"

	supportedSettings=(
		SynthDriver.VoiceSetting(),
		SynthDriver.RateSetting(),
		SynthDriver.RateBoostSetting(),
		SynthDriver.PitchSetting(),
		SynthDriver.InflectionSetting(),
		SynthDriver.VolumeSetting(),
	)
	supportedCommands = {
		IndexCommand,
		CharacterModeCommand,
		LangChangeCommand,
		BreakCommand,
		PitchCommand,
		RateCommand,
		VolumeCommand,
		PhonemeCommand,
	}
	supportedNotifications = {synthIndexReached, synthDoneSpeaking}

	@classmethod
	def check(cls):
		return True

	def __init__(self):
		_espeak_mb.initialize(self._onIndexReached)
		log.info("Using eSpeak with Mbrola version %s" % _espeak_mb.info())
		lang=languageHandler.getLanguage()
		_espeak_mb.setVoiceByLanguage(lang)
		self._language=lang
		self.rate=30
		self.pitch=50
		self.inflection=50

	def _get_language(self):
		return self._language

	PROSODY_ATTRS = {
		PitchCommand: "pitch",
		VolumeCommand: "volume",
		RateCommand: "rate",
	}

	IPA_TO_espeak = {
		u"θ": u"T",
		u"s": u"s",
		u"ˈ": u"'",
	}

	def _processText(self, text):
		# We need to make several replacements.
		return text.translate({
			0x1: None, # used for embedded commands
			0x3C: u"&lt;", # <: because of XML
			0x3E: u"&gt;", # >: because of XML
			0x5B: u" [", # [: [[ indicates phonemes
		})

	def speak(self,speechSequence):
		textList=[]
		prosody={}
		# We output malformed XML, as we might close an outer tag after opening an inner one; e.g.
		# <voice><prosody></voice></prosody>.
		# However, eSpeak doesn't seem to mind.
		for item in speechSequence:
			if isinstance(item,str):
				textList.append(self._processText(item))
			elif isinstance(item, IndexCommand):
				textList.append("<mark name=\"%d\" />"%item.index)
			elif isinstance(item, CharacterModeCommand):
				textList.append("<say-as interpret-as=\"characters\">" if item.state else "</say-as>")
			elif isinstance(item, BreakCommand):
				textList.append(f'<break time="{item.time}ms" />')
			elif type(item) in self.PROSODY_ATTRS:
				if prosody:
					# Close previous prosody tag.
					textList.append("</prosody>")
				attr=self.PROSODY_ATTRS[type(item)]
				if item.multiplier==1:
					# Returning to normal.
					try:
						del prosody[attr]
					except KeyError:
						pass
				else:
					prosody[attr]=int(item.multiplier* 100)
				if not prosody:
					continue
				textList.append("<prosody")
				for attr,val in prosody.items():
					textList.append(' %s="%d%%"'%(attr,val))
				textList.append(">")
			elif isinstance(item, PhonemeCommand):
				# We can't use str.translate because we want to reject unknown characters.
				try:
					phonemes="".join([self.IPA_TO_espeak_mb[char] for char in item.ipa])
					# There needs to be a space after the phoneme command.
					# Otherwise, eSpeak will announce a subsequent SSML tag instead of processing it.
					textList.append(u"[[%s]] "%phonemes)
				except KeyError:
					log.debugWarning("Unknown character in IPA string: %s"%item.ipa)
					if item.text:
						textList.append(self._processText(item.text))
			else:
				log.error("Unknown speech: %s"%item)
		# Close any open tags.
		if prosody:
			textList.append("</prosody>")
		text=u"".join(textList)
		_espeak_mb.speak(text)

	def cancel(self):
		_espeak_mb.stop()

	def pause(self,switch):
		_espeak_mb.pause(switch)

	_rateBoost = False
	RATE_BOOST_MULTIPLIER = 3

	def _get_rateBoost(self):
		return self._rateBoost

	def _set_rateBoost(self, enable):
		if enable == self._rateBoost:
			return
		rate = self.rate
		self._rateBoost = enable
		self.rate = rate

	def _get_rate(self):
		val=_espeak_mb.getParameter(_espeak_mb.espeakRATE,1)
		if self._rateBoost:
			val=int(val/self.RATE_BOOST_MULTIPLIER)
		return self._paramToPercent(val,_espeak_mb.minRate,_espeak_mb.maxRate)

	def _set_rate(self,rate):
		val=self._percentToParam(rate, _espeak_mb.minRate, _espeak_mb.maxRate)
		if self._rateBoost:
			val=int(val*self.RATE_BOOST_MULTIPLIER)
		_espeak_mb.setParameter(_espeak_mb.espeakRATE,val,0)

	def _get_pitch(self):
		val=_espeak_mb.getParameter(_espeak_mb.espeakPITCH,1)
		return self._paramToPercent(val,_espeak_mb.minPitch,_espeak_mb.maxPitch)

	def _set_pitch(self,pitch):
		val=self._percentToParam(pitch, _espeak_mb.minPitch, _espeak_mb.maxPitch)
		_espeak_mb.setParameter(_espeak_mb.espeakPITCH,val,0)

	def _get_inflection(self):
		val=_espeak_mb.getParameter(_espeak_mb.espeakRANGE,1)
		return self._paramToPercent(val,_espeak_mb.minPitch,_espeak_mb.maxPitch)

	def _set_inflection(self,val):
		val=self._percentToParam(val, _espeak_mb.minPitch, _espeak_mb.maxPitch)
		_espeak_mb.setParameter(_espeak_mb.espeakRANGE,val,0)

	def _get_volume(self):
		return _espeak_mb.getParameter(_espeak_mb.espeakVOLUME,1)

	def _set_volume(self,volume):
		_espeak_mb.setParameter(_espeak_mb.espeakVOLUME,volume,0)

	def _getAvailableVoices(self):
		voices=OrderedDict()
		for v in _espeak_mb.getVoiceList():
			l=_espeak_mb.decodeEspeakString(v.languages[1:])
			# #7167: Some languages names contain unicode characters EG: Norwegian Bokmål
			name=_espeak_mb.decodeEspeakString(v.name)
			# #5783: For backwards compatibility, voice identifies should always be lowercase
			identifier=os.path.basename(_espeak_mb.decodeEspeakString(v.identifier)).lower()
			voices[identifier]=VoiceInfo(identifier,name,l)
		return voices

	def _get_voice(self):
		curVoice=getattr(self,'_voice',None)
		if curVoice: return curVoice
		curVoice = _espeak_mb.getCurrentVoice()
		if not curVoice:
			return ""
		# #5783: For backwards compatibility, voice identifies should always be lowercase
		return _espeak_mb.decodeEspeakString(curVoice.identifier).split('+')[0].lower()

	def _set_voice(self, identifier):
		if not identifier:
			return
		# #5783: For backwards compatibility, voice identifies should always be lowercase
		identifier=identifier.lower()
		if "\\" in identifier:
			identifier=os.path.basename(identifier)
		self._voice=identifier
		try:
			_espeak_mb.setVoiceAndVariant(voice=identifier,variant="None")
		except:
			self._voice=None
			raise
		self._language=super(SynthDriver,self).language

	def _onIndexReached(self, index):
		if index is not None:
			synthIndexReached.notify(synth=self, index=index)
		else:
			synthDoneSpeaking.notify(synth=self)

	def terminate(self):
		_espeak_mb.terminate()


