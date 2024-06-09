# Espeak with Mbrola included #
* Autor: Felipe Porciuncula Zanabria
* Current version: 2.0 stable
* NVDA compatibility: from 2019.3 onwards.
* Download [for NVDA 2024.1](https://github.com/FelipeZanabria/Espeak-wit-Mbrola/releases/download/v2.0/espeakWitMbrola-2.0.nvda-addon)
* Download [for NVDA 2023.3.4 and older](https://github.com/FelipeZanabria/Espeak-wit-Mbrola/releases/download/v1.0.5/espeakWitMbrola-1.0.5.nvda-addon)
* [View source code on Github](https://github.com/FelipeZanabria/Espeak-wit-Mbrola)
This is the old Espeak with Mbrola support ported in an addon for NVDA.

## Features ##

* This add-on comes with an open source version of a Mbrola dll, found at: <https://github.com/numediart/MBROLA>. This version no longer shows the license agreement, which was very annoying as the screen reader voice stopped.
* In this distribution I have corrected the translations to Mbrola phonemes of the Brazilian Portuguese voices and the Spanish and dialects. Additionally, these voices are included in the add-on. The voices are: Br1, (known as the voice of the Virtual vision screen reader from Brazil, Br2 and 3, also created by the same company, and Br4, known as the Liane voice, which accompanies the Dosvox system.
For Spanish, there are the 4 voices of Spain, the 2 of Mexico and the Venezuelan one.
* This version handles sample frequency changes, when using a Mbrola voice. With the version that accompanied NVDA before Espeak-ng, it was possible to use these voices, but they sounded childish because the NVDA player did not switch to 16000 hz when necessary.
* Works 100% on portable copies of NVDA.
* It is lighter than the sapi5 version of Espeak.
* Variant setting and language switching have been removed because they were problematic. The first changes the sample rate and the second changes to a voice outside of Mbrola.
* Removed the native voices, so that the Mbrola voices can be found more easily, which is the main objective of this add-on.

## To add more Mbrola voices to the add-on ##

1. Check the voices supported by Espeak in: NVDA configuration folder/addons/espeakWithMbrola/synthDrivers/espeak-data/voices/mb
2. Download the Mbrola databases you want from: [here](https://github.com/numediart/MBROLA-voices)
3. Copy or move them to the path: NVDA configuration folder/addons/espeakWithMbrola/synthDrivers/espeak-data/mbrola.

## Known Issues ##

* Change pitch  for caps does not work when using a Mbrola voice. This is an eSpeak problem, because in the sapi5 version the pitch changes after the letter.
* At the end of some sentences there may be small glitches in the male voices, which I think may be because there is not enough silence for Mbrola to breathe. I have done some tests with the Serpro Liane tts program with 1 ms pauses and this happens.
