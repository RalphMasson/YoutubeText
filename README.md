
# Interface de Traitement des Vidéos YouTube et des Fichiers Audio

<p align="center">
  <img src="[https://github.com/RalphMasson/Rapporteur/blob/main/Geomathiques_Demo.gif](https://github.com/RalphMasson/YoutubeText/blob/main/YoutubeText_demo.jpg)" width="400" />
</p>

Cette application Python fournit une interface pour traiter des vidéos YouTube et des fichiers audio. Elle permet de récupérer des transcriptions de vidéos YouTube, de convertir des fichiers audio en format WAV, de les découper en segments plus petits, et de transcrire chaque segment en texte.

## Fonctionnalités

1. **Récupération de Transcriptions YouTube** :

   - Récupère les transcriptions des vidéos YouTube en utilisant la bibliothèque `YouTubeTranscriptApi`.
   - Traite automatiquement l'audio pour la transcription si la transcription n'est pas disponible.

2. **Conversion Audio** :

   - Convertit les fichiers MP3 en WAV à l'aide de `pydub`.
   - Conserve le fichier MP3 original tout en créant un fichier WAV.

3. **Découpage Audio** :

   - Découpe les fichiers WAV en segments d'une minute pour faciliter la transcription.

4. **Transcription Audio** :

   - Transcrit les segments audio en texte en utilisant l'API de reconnaissance vocale de Google (`speech_recognition`).

5. **Affichage Dynamique de la Progression** :

   - Affiche une barre de progression pour les étapes de conversion, de découpage et de transcription.
   - Met à jour l'interface avec les résultats de transcription en direct.

6. **Organisation par Session** :

   - Crée automatiquement un dossier de session pour chaque opération, contenant tous les fichiers générés (MP3, WAV, segments, transcription).

## Prérequis

- Python 3.8 ou version ultérieure
- Bibliothèques Python requises :
  - PyQt5
  - `pydub`
  - `speech_recognition`
  - `youtube-transcript-api`
  - `yt_dlp`
- FFmpeg installé et accessible via le PATH système pour le traitement audio.

## Installation

1. Clonez ou téléchargez ce dépôt.
2. Installez les bibliothèques Python requises :
   ```bash
   pip install PyQt5 pydub speechrecognition youtube-transcript-api yt-dlp
   ```
3. Installez FFmpeg :
   - Sur Windows : [Téléchargez FFmpeg](https://ffmpeg.org/download.html), extrayez-le et ajoutez le dossier `bin` au PATH système.
   - Sur Linux/macOS : Utilisez votre gestionnaire de paquets (par exemple, `sudo apt install ffmpeg` ou `brew install ffmpeg`).

## Comment Utiliser

1. Exécutez l'application :

   ```bash
   python nom_du_script.py
   ```

2. L'interface vous permet de :

   - Entrer une URL YouTube ou sélectionner un fichier audio.
   - Cliquer sur "Get YouTube Summary" pour récupérer la transcription ou traiter l'audio.
   - Cliquer sur "Process Audio" pour traiter manuellement le fichier audio sélectionné.

3. Résultats :

   - Les segments audio découpés sont sauvegardés dans un dossier `splits` dans le répertoire de session.
   - La transcription est sauvegardée dans un fichier `transcription.txt` dans le répertoire de session.

## Structure des Fichiers

- **`ConversionThread`** :
  Gère la conversion MP3 vers WAV dans un thread en arrière-plan.
- **`SplitThread`** :
  Découpe le fichier WAV en segments plus petits dans un thread en arrière-plan.
- **`TranscriptionThread`** :
  Traite chaque segment audio et le transcrit en texte.
- **`YouTubeSummaryApp`** :
  Interface principale de l'application PyQt5.

## Notes

- Assurez-vous que FFmpeg est correctement installé et accessible.
- Les fichiers audio ou vidéos de grande taille peuvent prendre du temps à être traités, selon leur durée et les performances de votre système.
- L'application utilise Google Speech Recognition, ce qui nécessite une connexion Internet active.

## Résolution des Problèmes

1. **FFmpeg Non Trouvé** :

   - Assurez-vous que FFmpeg est installé et ajouté au PATH système.

2. **Transcription YouTube Indisponible** :

   - L'application téléchargera et traitera automatiquement l'audio pour la transcription si la transcription n'est pas récupérable.

3. **Problèmes de Conversion Audio** :

   - Vérifiez que le fichier MP3 d'entrée est valide et non corrompu.

4. **Erreurs de Transcription** :

   - Vérifiez que votre connexion Internet est stable.

## Licence

Cette application est sous licence MIT. Consultez le fichier LICENSE pour plus de détails.

## Remerciements

- [PyQt5](https://riverbankcomputing.com/software/pyqt/intro)
- [pydub](https://github.com/jiaaro/pydub)
- [YouTubeTranscriptApi](https://github.com/jdepoix/youtube-transcript-api)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [FFmpeg](https://ffmpeg.org/)
