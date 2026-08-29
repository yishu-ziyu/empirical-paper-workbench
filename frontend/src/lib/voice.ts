export type VoiceStatus = 'idle' | 'listening' | 'unsupported' | 'denied'

type SpeechRecognitionCtor = new () => SpeechRecognitionLike

export type SpeechRecognitionLike = {
  lang: string
  continuous: boolean
  interimResults: boolean
  start: () => void
  stop: () => void
  abort: () => void
  onresult: ((ev: SpeechRecognitionResultEventLike) => void) | null
  onerror: ((ev: { error: string }) => void) | null
  onend: (() => void) | null
}

export type SpeechRecognitionResultEventLike = {
  resultIndex: number
  results: ArrayLike<{
    isFinal: boolean
    0: { transcript: string }
  }>
}

function recognitionCtor(): SpeechRecognitionCtor | null {
  const w = window as Window & {
    SpeechRecognition?: SpeechRecognitionCtor
    webkitSpeechRecognition?: SpeechRecognitionCtor
  }
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null
}

export function isSpeechRecognitionAvailable(): boolean {
  return typeof window !== 'undefined' && recognitionCtor() !== null
}

export function isSpeechSynthesisAvailable(): boolean {
  return typeof window !== 'undefined' && typeof window.speechSynthesis !== 'undefined'
}

export function createRecognizer(lang: string): SpeechRecognitionLike | null {
  const Ctor = recognitionCtor()
  if (!Ctor) return null
  const rec = new Ctor()
  rec.lang = lang
  rec.continuous = true
  rec.interimResults = true
  return rec
}

export function speak(text: string, lang: string): void {
  if (!isSpeechSynthesisAvailable() || !text.trim()) return
  window.speechSynthesis.cancel()
  const utter = new SpeechSynthesisUtterance(text.trim())
  utter.lang = lang.startsWith('zh') ? 'zh-CN' : 'en-US'
  utter.rate = 0.96
  window.speechSynthesis.speak(utter)
}

export function stopSpeaking(): void {
  if (!isSpeechSynthesisAvailable()) return
  window.speechSynthesis.cancel()
}

export function appendTranscript(prev: string, next: string): string {
  const incoming = next.trim()
  if (!incoming) return prev
  if (!prev.trim()) return incoming
  const needsSpace = !/\s$/.test(prev) && !/^[，。！？、,.!?]/.test(incoming)
  return needsSpace ? `${prev}${/[\u4e00-\u9fff]/.test(incoming) ? '' : ' '}${incoming}` : `${prev}${incoming}`
}
