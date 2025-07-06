import React from 'react';
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core';
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import {
  useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { QuestionResponse } from '@/lib/api';

interface ReorderableQuestionListProps {
  questions: QuestionResponse[];
  selectedQuestionIds: number[];
  onReorder: (newOrder: number[]) => void;
  onRemove: (questionId: number) => void;
  className?: string;
}

interface SortableQuestionItemProps {
  question: QuestionResponse;
  onRemove: (questionId: number) => void;
  index: number;
}

const SortableQuestionItem: React.FC<SortableQuestionItemProps> = ({
  question,
  onRemove,
  index,
}) => {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: question.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      criminal_background: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300',
      drug_use: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300',
      ethics: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300',
      dismissals: 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300',
      trustworthiness: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300',
      general: 'bg-gray-100 text-gray-800 dark:bg-gray-800/50 dark:text-gray-300',
    };
    return colors[category as keyof typeof colors] || colors.general;
  };

  const getImportanceColor = (importance: string) => {
    const colors = {
      mandatory: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300',
      ask_once: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300',
      optional: 'bg-gray-100 text-gray-800 dark:bg-gray-800/50 dark:text-gray-300',
    };
    return colors[importance as keyof typeof colors] || colors.optional;
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-start gap-3 p-4 bg-card border rounded-lg shadow-sm ${
        isDragging ? 'opacity-50 shadow-lg' : ''
      }`}
      data-testid={`sortable-question-${question.id}`}
    >
      {/* Order number */}
      <div className="flex-shrink-0 w-8 h-8 bg-muted rounded-full flex items-center justify-center text-sm font-medium text-muted-foreground">
        {index + 1}
      </div>

      {/* Drag handle */}
      <button
        {...attributes}
        {...listeners}
        className="flex-shrink-0 p-1 text-muted-foreground hover:text-foreground cursor-grab active:cursor-grabbing"
        data-testid={`drag-handle-${question.id}`}
      >
        <GripVertical className="h-4 w-4" />
      </button>

      {/* Question content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2 mb-2">
          <h4 className="font-medium text-sm leading-tight">{question.title}</h4>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onRemove(question.id)}
            className="flex-shrink-0 h-6 w-6 p-0 text-muted-foreground hover:text-destructive"
            data-testid={`remove-question-${question.id}`}
          >
            <X className="h-3 w-3" />
          </Button>
        </div>
        
        <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
          {question.question_text}
        </p>
        
        <div className="flex gap-2">
          <Badge variant="secondary" className={`text-xs ${getCategoryColor(question.category)}`}>
            {question.category.replace('_', ' ')}
          </Badge>
          <Badge variant="secondary" className={`text-xs ${getImportanceColor(question.importance)}`}>
            {question.importance.replace('_', ' ')}
          </Badge>
        </div>
      </div>
    </div>
  );
};

export const ReorderableQuestionList: React.FC<ReorderableQuestionListProps> = ({
  questions,
  selectedQuestionIds,
  onReorder,
  onRemove,
  className = '',
}) => {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Filter questions to only show selected ones in the correct order
  const selectedQuestions = selectedQuestionIds
    .map(id => questions.find(q => q.id === id))
    .filter((q): q is QuestionResponse => q !== undefined);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = selectedQuestionIds.indexOf(active.id as number);
      const newIndex = selectedQuestionIds.indexOf(over.id as number);
      
      const newOrder = arrayMove(selectedQuestionIds, oldIndex, newIndex);
      onReorder(newOrder);
    }
  };

  if (selectedQuestions.length === 0) {
    return (
      <div className={`text-center py-8 text-muted-foreground ${className}`}>
        <p>No questions selected. Select questions to see them here for reordering.</p>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="mb-4">
        <h3 className="text-sm font-medium mb-2">Selected Questions ({selectedQuestions.length})</h3>
        <p className="text-xs text-muted-foreground">
          Drag questions to reorder them. The order shown here will be used in the interview.
        </p>
      </div>
      
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        <SortableContext items={selectedQuestionIds} strategy={verticalListSortingStrategy}>
          <div className="space-y-2" data-testid="reorderable-question-list">
            {selectedQuestions.map((question, index) => (
              <SortableQuestionItem
                key={question.id}
                question={question}
                onRemove={onRemove}
                index={index}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>
    </div>
  );
};
