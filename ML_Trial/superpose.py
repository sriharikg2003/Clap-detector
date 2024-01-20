import librosa
import soundfile as sf

# Load audio files
sr = 44100


for i in range(100):
    audio1, sr1 = librosa.load('srihari_clap/'+str(i)+'.wav', sr=sr)
    audio2, sr2 = librosa.load('srihari_bg/'+str(i)+'.wav', sr=sr)
    # Adjust lengths
    min_len = min(len(audio1), len(audio2))
    audio1 = audio1[:min_len]
    audio2 = audio2[:min_len]

    superposed_audio = audio1 + audio2

    # Save the superposed audio using soundfile
    sf.write('srihari_superpose/'+str(i)+'.wav', superposed_audio, sr)
