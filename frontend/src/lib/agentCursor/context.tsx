import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import type { ResearchLab } from '../workspace'
import {
  AgentCursorPlayer,
  IDLE_PRESENTATION,
  type AgentCursorPresentation,
} from './player'
import { semanticTargetRegistry } from './registry'
import { prefersReducedMotion, resolvePreviewSpecId } from './previewSpec'
import {
  CARD_CHALLENGE_EXPERIENCE_SCRIPT,
  CARD_SHOW_ME_SCRIPT,
  type AgentScript,
} from './scripts'

export type AgentCursorApi = {
  presentation: AgentCursorPresentation
  playShowMe: () => void
  playChallengeExperience: () => void
  cancel: () => void
  pause: () => void
  resume: () => void
  replay: () => void
  confirmRunPreview: () => void
  reportDelta: (delta: { deltaAbs: number | null; deltaPct: number | null } | null) => void
}

const noopApi: AgentCursorApi = {
  presentation: IDLE_PRESENTATION,
  playShowMe: () => undefined,
  playChallengeExperience: () => undefined,
  cancel: () => undefined,
  pause: () => undefined,
  resume: () => undefined,
  replay: () => undefined,
  confirmRunPreview: () => undefined,
  reportDelta: () => undefined,
}

const AgentCursorContext = createContext<AgentCursorApi>(noopApi)

export function useAgentCursor(): AgentCursorApi {
  return useContext(AgentCursorContext)
}

export type AgentCursorHost = {
  workbenchTab: string
  research: ResearchLab | null | undefined
  onOpenEvidence: () => void
  onRunPreview: (specId: string) => Promise<void>
  onPromote?: () => Promise<void>
  moveTo: (el: Element, opts: { reduced: boolean }) => Promise<void>
  reducedMotion?: () => boolean
}

export function AgentCursorProvider({
  host,
  children,
}: {
  host: AgentCursorHost
  children: ReactNode
}) {
  const [presentation, setPresentation] = useState<AgentCursorPresentation>(IDLE_PRESENTATION)
  const hostRef = useRef(host)
  hostRef.current = host
  const mountedRef = useRef(true)
  const deltaRef = useRef<{ deltaAbs: number | null; deltaPct: number | null } | null>(null)
  const playerRef = useRef<AgentCursorPlayer | null>(null)

  if (playerRef.current == null) {
    playerRef.current = new AgentCursorPlayer({
      registry: semanticTargetRegistry,
      reducedMotion: () => hostRef.current.reducedMotion?.() ?? prefersReducedMotion(),
      moveTo: (el, opts) => hostRef.current.moveTo(el, opts),
      openEvidence: () => hostRef.current.onOpenEvidence(),
      runPreview: async (command) => {
        const specId = resolvePreviewSpecId(command, hostRef.current.research)
        if (!specId) return
        await hostRef.current.onRunPreview(specId)
      },
      promote: async () => {
        await hostRef.current.onPromote?.()
      },
      onPresentation: (next) => {
        if (!mountedRef.current) return
        setPresentation({ ...next })
      },
      clock: {
        sleep: (ms) => new Promise((resolve) => window.setTimeout(resolve, ms)),
      },
      readDelta: () => deltaRef.current,
    })
  }

  const play = useCallback((script: AgentScript) => {
    void playerRef.current?.play(script)
  }, [])

  const playShowMe = useCallback(() => {
    hostRef.current.onOpenEvidence()
    play(CARD_SHOW_ME_SCRIPT)
  }, [play])

  const playChallengeExperience = useCallback(() => {
    hostRef.current.onOpenEvidence()
    play(CARD_CHALLENGE_EXPERIENCE_SCRIPT)
  }, [play])

  const cancel = useCallback(() => {
    playerRef.current?.cancel()
  }, [])

  const pause = useCallback(() => {
    playerRef.current?.pause()
  }, [])

  const resume = useCallback(() => {
    playerRef.current?.resume()
  }, [])

  const replay = useCallback(() => {
    void playerRef.current?.replay()
  }, [])

  const confirmRunPreview = useCallback(() => {
    playerRef.current?.confirm('runPreview')
  }, [])

  const reportDelta = useCallback(
    (delta: { deltaAbs: number | null; deltaPct: number | null } | null) => {
      deltaRef.current = delta
    },
    [],
  )

  useEffect(() => {
    if (
      host.workbenchTab !== 'evidence' &&
      (presentation.status === 'running' ||
        presentation.status === 'paused' ||
        presentation.status === 'awaiting-confirm')
    ) {
      playerRef.current?.cancel()
    }
  }, [host.workbenchTab, presentation.status])

  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
      playerRef.current?.cancel()
    }
  }, [])

  useEffect(() => {
    const onPointer = (event: PointerEvent) => {
      if (playerRef.current?.state.status !== 'running') return
      const target = event.target
      if (target instanceof Element && target.closest('[data-agent-cursor-control]')) return
      playerRef.current.pause()
    }
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        playerRef.current?.cancel()
        return
      }
      if (playerRef.current?.state.status !== 'running') return
      playerRef.current.pause()
    }
    window.addEventListener('pointerdown', onPointer, true)
    window.addEventListener('keydown', onKey, true)
    return () => {
      window.removeEventListener('pointerdown', onPointer, true)
      window.removeEventListener('keydown', onKey, true)
    }
  }, [])

  const value = useMemo<AgentCursorApi>(
    () => ({
      presentation,
      playShowMe,
      playChallengeExperience,
      cancel,
      pause,
      resume,
      replay,
      confirmRunPreview,
      reportDelta,
    }),
    [
      presentation,
      playShowMe,
      playChallengeExperience,
      cancel,
      pause,
      resume,
      replay,
      confirmRunPreview,
      reportDelta,
    ],
  )

  return <AgentCursorContext.Provider value={value}>{children}</AgentCursorContext.Provider>
}
