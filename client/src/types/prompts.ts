/**
 * Centralized prompt type definitions and utilities
 */

export type PromptType = 'EVALUATION' | 'JUDGE' | 'GUARDRAILS' | 'QUESTION_EVALUATION';

export const PROMPT_TYPES = {
  EVALUATION: 'EVALUATION' as const,
  JUDGE: 'JUDGE' as const,
  GUARDRAILS: 'GUARDRAILS' as const,
  QUESTION_EVALUATION: 'QUESTION_EVALUATION' as const,
} as const;

export const PROMPT_TYPE_LABELS: Record<PromptType, string> = {
  EVALUATION: 'Evaluation',
  JUDGE: 'Judge',
  GUARDRAILS: 'Guardrails',
  QUESTION_EVALUATION: 'Question Evaluation',
} as const;

export const PROMPT_TYPE_DESCRIPTIONS: Record<PromptType, string> = {
  EVALUATION: 'Initial response generation using a smaller, faster model',
  JUDGE: 'Final response evaluation and refinement using a larger model',
  GUARDRAILS: 'Content safety and appropriateness checking',
  QUESTION_EVALUATION: 'Evaluating if interview questions were answered',
} as const;

export const PROMPT_TYPE_OPTIONS = [
  { 
    value: PROMPT_TYPES.EVALUATION, 
    label: PROMPT_TYPE_LABELS.evaluation, 
    description: PROMPT_TYPE_DESCRIPTIONS.evaluation 
  },
  { 
    value: PROMPT_TYPES.JUDGE, 
    label: PROMPT_TYPE_LABELS.judge, 
    description: PROMPT_TYPE_DESCRIPTIONS.judge 
  },
  { 
    value: PROMPT_TYPES.GUARDRAILS, 
    label: PROMPT_TYPE_LABELS.guardrails, 
    description: PROMPT_TYPE_DESCRIPTIONS.guardrails 
  },
  { 
    value: PROMPT_TYPES.QUESTION_EVALUATION, 
    label: PROMPT_TYPE_LABELS.question_evaluation, 
    description: PROMPT_TYPE_DESCRIPTIONS.question_evaluation 
  },
] as const;

/**
 * Get the human-readable label for a prompt type
 */
export function getPromptTypeLabel(promptType: PromptType): string {
  return PROMPT_TYPE_LABELS[promptType] || promptType;
}

/**
 * Get the description for a prompt type
 */
export function getPromptTypeDescription(promptType: PromptType): string {
  return PROMPT_TYPE_DESCRIPTIONS[promptType] || '';
}

/**
 * Check if a string is a valid prompt type
 */
export function isValidPromptType(value: string): value is PromptType {
  return Object.values(PROMPT_TYPES).includes(value as PromptType);
}
