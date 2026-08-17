export type JourneyStageStatus = 'pending' | 'active' | 'completed' | 'interrupt'

export interface JourneyStage {
  status: JourneyStageStatus
  canIntervene: boolean
}

export interface JourneyProgress {
  currentStage: number
  stages: JourneyStage[]
}