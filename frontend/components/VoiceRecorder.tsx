"use client";

import { useEffect, useRef, useState } from "react";
import { analyzeVoice, ApiError, type ModalityResult } from "@/lib/api";
import { blobToWav } from "@/lib/wav";

type Status = "idle" | "recording" | "ready" | "analyzing";

const MAX_SECONDS = 20;

export default function VoiceRecorder({ onScore }: { onScore?: (score: number | null) => void }) {
  const [status, setStatus] = useState<Status>("idle");
  const [seconds, setSeconds] = useState(0);
  const [audio, setAudio] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ModalityResult | null>(null);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const elapsedRef = useRef(0);

  useEffect(() => {
    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [audioUrl]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      recorderRef.current?.stream.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const setRecording = (blob: Blob) => {
    setAudio(blob);
    setAudioUrl(URL.createObjectURL(blob));
    setStatus("ready");
  };

  const reset = () => {
    setAudio(null);
    setAudioUrl(null);
    setResult(null);
    onScore?.(null);
    setError(null);
    setSeconds(0);
    setStatus("idle");
  };

  const stop = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    const recorder = recorderRef.current;
    if (recorder && recorder.state === "recording") recorder.stop();
  };

  const start = async () => {
    reset();
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setError("Recording is not available in this browser. Please upload an audio file instead.");
      return;
    }
    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setError("Microphone access was denied or no microphone was found. You can upload a file instead.");
      return;
    }
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];
    recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
    recorder.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
      setRecording(new Blob(chunksRef.current, { type: recorder.mimeType }));
    };
    recorderRef.current = recorder;
    recorder.start();
    setStatus("recording");
    elapsedRef.current = 0;
    timerRef.current = setInterval(() => {
      elapsedRef.current += 1;
      setSeconds(elapsedRef.current);
      if (elapsedRef.current >= MAX_SECONDS) stop();
    }, 1000);
  };

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    reset();
    setRecording(file);
  };

  const analyze = async () => {
    if (!audio) return;
    setStatus("analyzing");
    setError(null);
    try {
      const wav = await blobToWav(audio);
      const r = await analyzeVoice(wav);
      setResult(r);
      onScore?.(r.score);
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "This audio could not be decoded. Try recording again or upload a different file.",
      );
    } finally {
      setStatus("ready");
    }
  };

  const btn =
    "rounded-md px-5 py-2.5 font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-50";

  return (
    <div>
      <p className="text-muted">
        Take a breath and say a steady &ldquo;ahhh&rdquo; for as long as is comfortable, in a quiet
        room.
      </p>

      <div className="mt-4 flex flex-wrap items-center gap-3">
        {status !== "recording" ? (
          <button
            onClick={start}
            disabled={status === "analyzing"}
            className={`${btn} bg-accent text-accent-ink hover:bg-[#0a5560]`}
          >
            {audio ? "Record again" : "Start recording"}
          </button>
        ) : (
          <button onClick={stop} className={`${btn} bg-ink text-white`}>
            Stop ({seconds}s)
          </button>
        )}

        <label
          className={`${btn} cursor-pointer border border-line bg-white text-ink hover:bg-paper has-[:disabled]:cursor-not-allowed`}
        >
          Upload audio file
          <input
            type="file"
            accept="audio/*"
            className="sr-only"
            onChange={onFile}
            disabled={status === "recording" || status === "analyzing"}
          />
        </label>
      </div>

      {status === "recording" && (
        <p className="mt-3 text-sm text-muted" role="status">
          Recording… it stops automatically after {MAX_SECONDS} seconds.
        </p>
      )}

      {audioUrl && status !== "recording" && (
        <div className="mt-4">
          <audio controls src={audioUrl} className="w-full max-w-md" />
          <button
            onClick={analyze}
            disabled={status === "analyzing"}
            className={`${btn} mt-4 bg-accent text-accent-ink hover:bg-[#0a5560]`}
          >
            {status === "analyzing" ? "Analysing…" : "Analyse recording"}
          </button>
        </div>
      )}

      {error && (
        <p role="alert" className="mt-4 border-l-4 border-red-600 bg-red-50 px-4 py-3 text-sm text-red-900">
          {error}
        </p>
      )}

      {result && (
        <div className="mt-4" role="status">
          <p className="text-lg">
            Voice screening signal: <strong>{Math.round(result.score * 100)}</strong> / 100
          </p>
          {result.note && <p className="mt-1 text-sm text-slate-600">{result.note}</p>}
        </div>
      )}
    </div>
  );
}
