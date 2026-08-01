import { useEffect, useState } from 'react'
import { useT } from '../lib/i18n'

/**
 * CHARLS dataset native wizard (T-11).
 *
 * Renders when the backend profiling step detects that the uploaded CSV is
 * a CHARLS extract. The user reviews the suggested variable mapping (CHARLS
 * code → readable name), picks survey waves, and applies any filter preset.
 * On confirm, the resolved configuration is passed to ``onConfirm`` so the
 * caller can write it into the LangGraph state — subsequent nodes then use
 * the readable variable names.
 */

export interface CharlsFilterCondition {
  col?: string
  op?: string
  val?: number | string
  type?: string
}

export interface CharlsFilterPreset {
  name: string
  conditions: CharlsFilterCondition[]
}

export interface CharlsIdentifier {
  required_columns: string[]
  pattern_columns: string[]
  min_pattern_matches: number
}

export interface CharlsConfig {
  name: string
  identifier: CharlsIdentifier
  variable_mapping: Record<string, string>
  waves: number[]
  default_waves: number[]
  filter_presets: CharlsFilterPreset[]
}

export interface CharlsConfirmPayload {
  variable_mapping: Record<string, string>
  waves: number[]
  filter_presets: CharlsFilterPreset[]
}

interface CharlsWizardProps {
  isOpen: boolean
  config: CharlsConfig
  onConfirm: (payload: CharlsConfirmPayload) => void
  onClose: () => void
}

export default function CharlsWizard({
  isOpen,
  config,
  onConfirm,
  onClose,
}: CharlsWizardProps) {
  const { t } = useT()
  // Variable mapping: editable copy of config.variable_mapping.
  const [mapping, setMapping] = useState<Record<string, string>>({})
  // Selected waves: initialized from config.default_waves.
  const [selectedWaves, setSelectedWaves] = useState<number[]>([])
  // Applied filter presets: tracked by name.
  const [appliedPresets, setAppliedPresets] = useState<string[]>([])

  // Initialize state whenever the wizard is (re)opened or config changes.
  useEffect(() => {
    if (isOpen && config) {
      setMapping({ ...config.variable_mapping })
      setSelectedWaves([...config.default_waves])
      setAppliedPresets([])
    }
  }, [isOpen, config])

  if (!isOpen || !config) {
    return null
  }

  const mappingEntries = Object.entries(mapping)

  const toggleWave = (wave: number) => {
    setSelectedWaves((prev) =>
      prev.includes(wave) ? prev.filter((w) => w !== wave) : [...prev, wave].sort(),
    )
  }

  const togglePreset = (presetName: string) => {
    setAppliedPresets((prev) =>
      prev.includes(presetName)
        ? prev.filter((p) => p !== presetName)
        : [...prev, presetName],
    )
  }

  const handleMappingChange = (code: string, value: string) => {
    setMapping((prev) => ({ ...prev, [code]: value }))
  }

  const handleConfirm = () => {
    const selectedPresetObjects = config.filter_presets.filter((p) =>
      appliedPresets.includes(p.name),
    )
    onConfirm({
      variable_mapping: mapping,
      waves: [...selectedWaves].sort(),
      filter_presets: selectedPresetObjects,
    })
  }

  return (
    <div
      data-testid="charls-wizard"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    >
      <div className="max-h-[90vh] w-[min(720px,90vw)] overflow-y-auto rounded-lg bg-white p-6 shadow-xl">
        <header className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            {t('charls.title')}
          </h2>
          <button
            data-testid="charls-cancel-btn"
            onClick={onClose}
            className="rounded px-2 py-1 text-sm text-gray-500 hover:bg-gray-100"
          >
            {t('charls.cancel')}
          </button>
        </header>

        {/* Section 1: variable mapping table */}
        <section
          data-testid="variable-mapping-table"
          className="mb-6 rounded border border-gray-200 p-3"
        >
          <h3 className="mb-2 text-sm font-semibold">{t('charls.mapping')}</h3>
          <div className="max-h-64 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-white">
                <tr className="border-b text-left">
                  <th className="py-1 pr-2">{t('charls.originalVar')}</th>
                  <th className="py-1">{t('charls.readableVar')}</th>
                </tr>
              </thead>
              <tbody>
                {mappingEntries.map(([code, readable]) => (
                  <tr
                    key={code}
                    data-testid={`mapping-row-${code}`}
                    className="border-b"
                  >
                    <td className="py-1 pr-2 font-mono text-gray-700">{code}</td>
                    <td className="py-1">
                      <input
                        type="text"
                        value={readable}
                        data-testid={`mapping-input-${code}`}
                        onChange={(e) =>
                          handleMappingChange(code, e.target.value)
                        }
                        className="w-full rounded border border-gray-300 px-2 py-1 font-mono text-sm focus:border-blue-500 focus:outline-none"
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 2: wave selection */}
        <section
          data-testid="waves-section"
          className="mb-6 rounded border border-gray-200 p-3"
        >
          <h3 className="mb-2 text-sm font-semibold">{t('charls.waves')}</h3>
          <div className="flex flex-wrap gap-3">
            {config.waves.map((wave) => {
              const checked = selectedWaves.includes(wave)
              return (
                <label
                  key={wave}
                  className="flex items-center gap-1 text-sm"
                >
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => toggleWave(wave)}
                    data-testid={`wave-checkbox-${wave}`}
                  />
                  <span>{wave}</span>
                </label>
              )
            })}
          </div>
        </section>

        {/* Section 3: filter presets */}
        <section
          data-testid="filter-presets-section"
          className="mb-6 rounded border border-gray-200 p-3"
        >
          <h3 className="mb-2 text-sm font-semibold">{t('charls.presets')}</h3>
          <div className="flex flex-wrap gap-2">
            {config.filter_presets.map((preset) => {
              const active = appliedPresets.includes(preset.name)
              return (
                <button
                  key={preset.name}
                  data-testid={`filter-preset-${preset.name}`}
                  onClick={() => togglePreset(preset.name)}
                  className={`rounded px-3 py-1 text-sm ${
                    active
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {preset.name}
                </button>
              )
            })}
          </div>
        </section>

        {/* Footer actions */}
        <footer className="flex justify-end gap-2 border-t pt-3">
          <button
            data-testid="charls-confirm-btn"
            onClick={handleConfirm}
            className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            {t('charls.confirm')}
          </button>
        </footer>
      </div>
    </div>
  )
}
