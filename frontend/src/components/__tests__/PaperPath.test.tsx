import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import type { ComponentProps } from 'react'
import PaperPath from '../PaperPath'
import { I18nProvider } from '../../lib/i18n'
import { CLEAN_STEPS, PAPER_NODES, derivePaperPath } from '../../lib/paperPath'

function renderPath(props: Partial<ComponentProps<typeof PaperPath>> = {}) {
  return render(
    <I18nProvider>
      <PaperPath
        uploading={false}
        hasSession={false}
        hasDirection={false}
        directionOpen
        hasReadout={false}
        hasOutline={false}
        writing={false}
        hasChapter={false}
        awaitingApprove={false}
        canExport={false}
        {...props}
      />
    </I18nProvider>,
  )
}

describe('PaperPath 右栏步骤', () => {
  test('shows the locked paper-path nodes and the 8 clean_data steps', () => {
    renderPath()
    expect(screen.getByTestId('paper-path')).toBeInTheDocument()
    for (const id of PAPER_NODES) {
      expect(screen.getByTestId(`paper-path-${id}`)).toBeInTheDocument()
    }
    for (const id of CLEAN_STEPS) {
      expect(screen.getByTestId(`clean-step-${id}`)).toBeInTheDocument()
    }
    expect(screen.queryByTestId('paper-path-generate_title')).not.toBeInTheDocument()
    expect(screen.queryByTestId('paper-path-identification_verify')).not.toBeInTheDocument()
    expect(screen.queryByTestId('paper-path-search_literature')).not.toBeInTheDocument()
    expect(screen.queryByTestId('paper-path-eda')).not.toBeInTheDocument()
  })

  test('pauses set_direction until the form is submitted', () => {
    const derived = derivePaperPath({
      uploading: false,
      hasSession: true,
      hasDirection: false,
      directionOpen: true,
      hasReadout: false,
      hasOutline: false,
      writing: false,
      hasChapter: false,
      awaitingApprove: false,
      canExport: false,
    })
    expect(derived.nodes.upload_data).toBe('completed')
    expect(derived.nodes.clean_data).toBe('pending')
    expect(derived.nodes.set_direction).toBe('paused')
    expect(derived.clean.profiling).toBe('pending')
    expect(derived.clean.audit).toBe('pending')
  })

  test('pauses generate_chapter until the chapter is written or approved', () => {
    renderPath({
      hasSession: true,
      hasDirection: true,
      directionOpen: false,
      hasReadout: true,
      hasOutline: true,
    })
    expect(screen.getByTestId('paper-path-generate_chapter')).toHaveAttribute('data-status', 'paused')
  })

  test('pauses a clean_data HITL sub-step without adding extra stations', () => {
    const derived = derivePaperPath({
      uploading: false,
      hasSession: true,
      hasDirection: false,
      directionOpen: true,
      hasReadout: false,
      hasOutline: false,
      writing: false,
      hasChapter: false,
      awaitingApprove: false,
      canExport: false,
      cleaningSteps: [
        { name: 'ProfilingStep', status: 'success' },
        { name: 'merge', status: 'success' },
        { name: 'MissingStep', status: 'paused' },
      ],
    })
    expect(derived.nodes.clean_data).toBe('paused')
    expect(derived.clean.profiling).toBe('completed')
    expect(derived.clean.merge).toBe('completed')
    expect(derived.clean.missing).toBe('paused')
    expect(derived.clean.outliers).toBe('pending')
    expect(derived.clean.audit).toBe('pending')

    renderPath({
      hasSession: true,
      cleaningSteps: [
        { name: 'profiling', status: 'success' },
        { name: 'merge', status: 'success' },
        { name: 'missing', status: 'paused' },
      ],
    })
    expect(screen.getByTestId('paper-path-clean_data')).toHaveAttribute('data-status', 'paused')
    expect(screen.getByTestId('clean-step-missing')).toHaveAttribute('data-status', 'paused')
    expect(screen.queryByTestId('paper-path-eda')).not.toBeInTheDocument()
  })
})
