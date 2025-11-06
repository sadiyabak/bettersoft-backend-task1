// src/components/TaskList.tsx
// Main component that displays list of tasks with actions
import React, { useEffect, useState } from 'react';
import { Task, taskApi } from '../api/api';
import './TaskList.css';

interface TaskListProps {
  onSelectTask: (taskId: number) => void;
  onEditTask: (task: Task) => void;
}

const TaskList: React.FC<TaskListProps> = ({ onSelectTask, onEditTask }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loadingTasks, setLoadingTasks] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  // Load tasks on component mount
  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      setLoadingTasks(true);
      setErrorMessage(null);
      const data = await taskApi.getAllTasks();
      setTasks(data);
    } catch (error) {
      setErrorMessage('Failed to load tasks. Please try again.');
      console.error('Error loading tasks:', error);
    } finally {
      setLoadingTasks(false);
    }
  };

  const handleDeleteTask = async (id: number) => {
    // Simple confirmation dialog
    const confirmed = window.confirm('Are you sure you want to delete this task?');
    if (!confirmed) return;

    try {
      setDeletingId(id);
      await taskApi.deleteTask(id);
      // Remove from local state immediately (optimistic update)
      setTasks(tasks.filter(task => task.id !== id));
    } catch (error) {
      setErrorMessage('Failed to delete task. Please try again.');
      console.error('Error deleting task:', error);
    } finally {
      setDeletingId(null);
    }
  };

  if (loadingTasks) {
    return (
      <div className="task-list-container">
        <div className="spinner">Loading tasks...</div>
      </div>
    );
  }

  return (
    <div className="task-list-container">
      <h2>My Tasks</h2>
      
      {errorMessage && (
        <div className="error-message">{errorMessage}</div>
      )}

      {tasks.length === 0 ? (
        <p className="empty-state">No tasks yet. Create one to get started!</p>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <li key={task.id} className="task-item">
              <div className="task-content" onClick={() => onSelectTask(task.id)}>
                <h3>{task.title}</h3>
                {task.description && <p>{task.description}</p>}
                <span className="task-status">{task.status || 'pending'}</span>
              </div>
              <div className="task-actions">
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    onEditTask(task);
                  }}
                  className="btn-edit"
                >
                  Edit
                </button>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteTask(task.id);
                  }}
                  className="btn-delete"
                  disabled={deletingId === task.id}
                >
                  {deletingId === task.id ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default TaskList;