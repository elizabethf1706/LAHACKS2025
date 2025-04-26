type AudioFrameData = {
  audioFrame: Float32Array;
  audioFrameShape: vec3;
};

const SAMPLE_RATE = 16000;

const remoteServiceModule = require("LensStudio:RemoteServiceModule");

@component
export class MicrophoneRecorder extends BaseScriptComponent {
  @input
  microphoneAsset: AudioTrackAsset;

  @input
  audioOutput: AudioTrackAsset;

  @input
  private outputTextComponent: Text;

  @input
  @allowUndefined
  debugText: Text;

  private audioComponent: AudioComponent;
  private recordAudioUpdateEvent: UpdateEvent;
  private playbackAudioUpdateEvent: UpdateEvent;

  private microphoneControl: MicrophoneAudioProvider;
  private audioOutputProvider: AudioOutputProvider;

  private recordedAudioFrames: AudioFrameData[] = [];

  private numberOfSamples: number = 0;
  private _recordingDuration: number = 0;

  private currentPlaybackTime: number = 0;

  private silenceTimer: number = 0;
  private readonly SILENCE_THRESHOLD = 0.03; // adjust based on testing
  private readonly MAX_SILENCE_DURATION = 0.5; // seconds

  private justStarted: boolean = true;

  onAwake() {
    // Initialize microphone control and set sample rate
    this.microphoneControl = this.microphoneAsset
      .control as MicrophoneAudioProvider;
    this.microphoneControl.sampleRate = SAMPLE_RATE;

    // Create and configure audio component
    this.audioComponent = this.sceneObject.createComponent("AudioComponent");
    this.audioComponent.audioTrack = this.audioOutput;
    this.audioOutputProvider = this.audioOutput.control as AudioOutputProvider;
    this.audioOutputProvider.sampleRate = SAMPLE_RATE;

    // Create and bind record audio update event
    this.recordAudioUpdateEvent = this.createEvent("UpdateEvent");
    this.recordAudioUpdateEvent.bind(() => {
      this.onRecordAudio();
    });
    this.recordAudioUpdateEvent.enabled = false;

    // Create and bind playback audio update event
    this.playbackAudioUpdateEvent = this.createEvent("UpdateEvent");
    this.playbackAudioUpdateEvent.bind(() => {
      this.onPlaybackAudio();
    });
    this.playbackAudioUpdateEvent.enabled = false;

    this.recordMicrophoneAudio(true);
  }

  // Called to record audio from the microphone
  private onRecordAudio() {
    let frameSize: number = this.microphoneControl.maxFrameSize;
    let audioFrame = new Float32Array(frameSize);

    // Get audio frame shape
    const audioFrameShape = this.microphoneControl.getAudioFrame(audioFrame);

    // If no audio data, return early
    if (audioFrameShape.x === 0) {
      return;
    }

    // Reduce the initial subarray size to the audioFrameShape value
    audioFrame = audioFrame.subarray(0, audioFrameShape.x);

    // Update the number of samples and recording duration
    this.numberOfSamples += audioFrameShape.x;
    this._recordingDuration = this.numberOfSamples / SAMPLE_RATE;

    const rms = this.calculateRMS(audioFrame);
    if (rms < this.SILENCE_THRESHOLD) {
      this.silenceTimer += getDeltaTime();
      if (this.silenceTimer >= this.MAX_SILENCE_DURATION && !this.justStarted) {
        this.stopRecordingDueToSilence();
      }
    } else {
      print("voice detected");
      this.silenceTimer = 0; // reset timer if voice detected
      this.justStarted = false;
    }

    // Update debug text with recording information
    this.updateRecordingDebugText();

    // Store the recorded audio frame
    this.recordedAudioFrames.push({
      audioFrame: audioFrame,
      audioFrameShape: audioFrameShape,
    });
  }

  // Called to handle playback of recorded audio
  private onPlaybackAudio() {
    this.currentPlaybackTime += getDeltaTime();
    this.currentPlaybackTime = Math.min(
      this.currentPlaybackTime,
      this._recordingDuration
    );

    // Update debug text with playback information
    this.updatePlaybackDebugText();

    // Stop playback if the end of the recording is reached
    if (this.currentPlaybackTime >= this._recordingDuration) {
      this.audioComponent.stop(false);
      this.playbackAudioUpdateEvent.enabled = false;
    }
  }

  // Update the debug text with recording information
  updateRecordingDebugText() {
    if (isNull(this.debugText)) {
      return;
    }

    this.debugText.text =
      "Duration: " + this._recordingDuration.toFixed(1) + "s";
    this.debugText.text +=
      "\n Size: " + (this.getTotalRecordedBytes() / 1000).toFixed(1) + "kB";
    this.debugText.text += "\nSample Rate: " + SAMPLE_RATE;
  }

  // Update the debug text with playback information
  updatePlaybackDebugText() {
    if (this.numberOfSamples <= 0) {
      this.debugText.text =
        "Oops! \nNo audio has been recorded yet. Please try recording again.";
      return;
    }

    this.debugText.text = "Playback Time: \n";
    this.debugText.text +=
      this.currentPlaybackTime.toFixed(1) +
      "s / " +
      this._recordingDuration.toFixed(1) +
      "s";
  }

  // Start or stop recording audio from the microphone
  recordMicrophoneAudio(toRecord: boolean) {
    if (toRecord) {
      print("Start recording?");
      this.justStarted = true;
      this.recordedAudioFrames = [];
      this.audioComponent.stop(false);
      this.numberOfSamples = 0;
      this.microphoneControl.start();
      this.recordAudioUpdateEvent.enabled = true;
      this.playbackAudioUpdateEvent.enabled = false;
    } else {
      this.microphoneControl.stop();
      this.recordAudioUpdateEvent.enabled = false;
    }
  }

  // Start playback of the recorded audio
  playbackRecordedAudio(): boolean {
    this.updatePlaybackDebugText();
    if (this.recordedAudioFrames.length <= 0) {
      return false;
    }
    this.currentPlaybackTime = 0;
    this.audioComponent.stop(false);
    this.playbackAudioUpdateEvent.enabled = true;
    this.audioComponent.play(-1);
    for (let i = 0; i < this.recordedAudioFrames.length; i++) {
      this.audioOutputProvider.enqueueAudioFrame(
        this.recordedAudioFrames[i].audioFrame,
        this.recordedAudioFrames[i].audioFrameShape
      );
    }
    return true;
  }

  // Getter for recording duration
  public get recordingDuration(): number {
    return this._recordingDuration;
  }

  // Calculate the total recorded bytes
  private getTotalRecordedBytes(): number {
    let totalBytes = 0;
    for (const frame of this.recordedAudioFrames) {
      totalBytes += frame.audioFrame.byteLength;
    }
    return totalBytes;
  }

  private calculateRMS(frame: Float32Array): number {
    let sumSquares = 0;
    for (let i = 0; i < frame.length; i++) {
      sumSquares += frame[i] * frame[i];
    }
    return Math.sqrt(sumSquares / frame.length);
  }

  private async sendData() {
    const data = this.recordedAudioFrames.map((prev) => Array.from(prev.audioFrame)).reduce((a, b) => a.concat(b), []);

    const headers = {
      "Content-Type": "application/json",
    };

    print("preparing req")

    const request = new Request("https://la-hacks-2025-backend.onrender.com/api/audio-response", {
        method: "POST",
        headers,
        body: JSON.stringify(data),
    });

    print("sending req")

    const response = await remoteServiceModule.fetch(request);

    print("sent req ");

    const responseJson = await response.json();

    

    // todo: maybe some error handling here
    this.outputTextComponent.text = responseJson.response;
  }
  
  private stopRecordingDueToSilence() {
    print("Stopped recording: silence detected");
    this.recordMicrophoneAudio(false);
    this.sendData();
    this.recordMicrophoneAudio(true);
  }
}