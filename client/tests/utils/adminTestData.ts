/**
 * Test data utilities for admin dashboard tests
 * Provides consistent test data across all test suites
 */

export interface TestCandidate {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
}

export interface TestInterview {
  candidateId: number;
  jobId: number;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  passKey?: string;
  score?: number;
  integrityScore?: 'low' | 'medium' | 'high';
  riskLevel?: 'low' | 'medium' | 'high' | 'critical';
}

export interface TestQuestion {
  title: string;
  questionText: string;
  instructions?: string;
  importance: 'optional' | 'ask_once' | 'mandatory';
  category: 'criminal_background' | 'drug_use' | 'ethics' | 'dismissals' | 'trustworthiness' | 'general';
}

export interface TestJob {
  title: string;
  description?: string;
  department?: string;
}

export interface TestUser {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: 'admin' | 'user';
}

/**
 * Test Candidates Data
 */
export const testCandidates = {
  valid: {
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@test.com',
    phone: '+1234567890'
  } as TestCandidate,
  
  minimal: {
    firstName: 'Jane',
    lastName: 'Smith',
    email: 'jane.smith@test.com'
  } as TestCandidate,
  
  withSpecialChars: {
    firstName: 'María',
    lastName: "O'Connor",
    email: 'maria.oconnor@test.com',
    phone: '+1-555-123-4567'
  } as TestCandidate,
  
  longNames: {
    firstName: 'Christopher',
    lastName: 'Vandenberghe-Williams',
    email: 'christopher.vandenberghe-williams@verylongdomainname.com',
    phone: '+1 (555) 123-4567 ext. 1234'
  } as TestCandidate,
  
  batch: [
    {
      firstName: 'Alice',
      lastName: 'Johnson',
      email: 'alice.johnson@test.com',
      phone: '+1234567891'
    },
    {
      firstName: 'Bob',
      lastName: 'Wilson',
      email: 'bob.wilson@test.com',
      phone: '+1234567892'
    },
    {
      firstName: 'Carol',
      lastName: 'Brown',
      email: 'carol.brown@test.com',
      phone: '+1234567893'
    },
    {
      firstName: 'David',
      lastName: 'Davis',
      email: 'david.davis@test.com',
      phone: '+1234567894'
    },
    {
      firstName: 'Eva',
      lastName: 'Miller',
      email: 'eva.miller@test.com',
      phone: '+1234567895'
    }
  ] as TestCandidate[],
  
  invalid: {
    emptyFirstName: {
      firstName: '',
      lastName: 'Doe',
      email: 'test@test.com'
    },
    emptyLastName: {
      firstName: 'John',
      lastName: '',
      email: 'test@test.com'
    },
    invalidEmail: {
      firstName: 'John',
      lastName: 'Doe',
      email: 'invalid-email'
    },
    duplicateEmail: {
      firstName: 'John',
      lastName: 'Duplicate',
      email: 'john.doe@test.com' // Same as valid candidate
    }
  }
};

/**
 * Test Jobs Data
 */
export const testJobs = {
  softwareEngineer: {
    title: 'Software Engineer',
    description: 'Develop and maintain software applications',
    department: 'Engineering'
  } as TestJob,
  
  accountant: {
    title: 'Senior Accountant',
    description: 'Manage financial records and reporting',
    department: 'Finance'
  } as TestJob,
  
  salesManager: {
    title: 'Sales Manager',
    description: 'Lead sales team and drive revenue growth',
    department: 'Sales'
  } as TestJob,
  
  hrSpecialist: {
    title: 'HR Specialist',
    description: 'Handle recruitment and employee relations',
    department: 'Human Resources'
  } as TestJob,
  
  batch: [
    {
      title: 'Marketing Coordinator',
      description: 'Coordinate marketing campaigns and events',
      department: 'Marketing'
    },
    {
      title: 'Customer Support Representative',
      description: 'Provide customer service and technical support',
      department: 'Support'
    },
    {
      title: 'Data Analyst',
      description: 'Analyze data and create reports',
      department: 'Analytics'
    }
  ] as TestJob[]
};

/**
 * Test Questions Data
 */
export const testQuestions = {
  criminalBackground: {
    title: 'Criminal History Disclosure',
    questionText: 'Have you ever been convicted of a felony or misdemeanor?',
    instructions: 'Please be honest and provide details if applicable',
    importance: 'mandatory' as const,
    category: 'criminal_background' as const
  } as TestQuestion,
  
  drugUse: {
    title: 'Substance Use History',
    questionText: 'Have you used illegal drugs in the past 5 years?',
    instructions: 'This information is confidential and used for safety purposes',
    importance: 'ask_once' as const,
    category: 'drug_use' as const
  } as TestQuestion,
  
  ethics: {
    title: 'Ethical Scenario',
    questionText: 'How would you handle discovering a coworker stealing from the company?',
    instructions: 'Describe your thought process and actions',
    importance: 'mandatory' as const,
    category: 'ethics' as const
  } as TestQuestion,
  
  dismissals: {
    title: 'Employment Termination',
    questionText: 'Have you ever been terminated or asked to resign from a position?',
    instructions: 'Please explain the circumstances if applicable',
    importance: 'ask_once' as const,
    category: 'dismissals' as const
  } as TestQuestion,
  
  trustworthiness: {
    title: 'Trust and Reliability',
    questionText: 'Describe a situation where you had to maintain confidentiality.',
    instructions: 'Focus on your approach to handling sensitive information',
    importance: 'optional' as const,
    category: 'trustworthiness' as const
  } as TestQuestion,
  
  general: {
    title: 'General Background',
    questionText: 'Tell us about your professional background and goals.',
    instructions: 'Keep your response concise and relevant',
    importance: 'optional' as const,
    category: 'general' as const
  } as TestQuestion
};

/**
 * Test Interviews Data
 */
export const testInterviews = {
  pending: {
    candidateId: 1,
    jobId: 1,
    status: 'pending' as const,
    passKey: 'TEST123ABC'
  } as TestInterview,
  
  inProgress: {
    candidateId: 2,
    jobId: 1,
    status: 'in_progress' as const,
    passKey: 'TEST456DEF'
  } as TestInterview,
  
  completed: {
    candidateId: 3,
    jobId: 2,
    status: 'completed' as const,
    passKey: 'TEST789GHI',
    score: 85,
    integrityScore: 'high' as const,
    riskLevel: 'low' as const
  } as TestInterview,
  
  cancelled: {
    candidateId: 4,
    jobId: 2,
    status: 'cancelled' as const,
    passKey: 'TEST012JKL'
  } as TestInterview,
  
  highRisk: {
    candidateId: 5,
    jobId: 3,
    status: 'completed' as const,
    passKey: 'TEST345MNO',
    score: 45,
    integrityScore: 'low' as const,
    riskLevel: 'critical' as const
  } as TestInterview
};

/**
 * Test Users Data
 */
export const testUsers = {
  admin: {
    email: 'admin@test.com',
    password: 'TestAdmin123!',
    firstName: 'Admin',
    lastName: 'User',
    role: 'admin' as const
  } as TestUser,
  
  regularUser: {
    email: 'user@test.com',
    password: 'TestUser123!',
    firstName: 'Regular',
    lastName: 'User',
    role: 'user' as const
  } as TestUser
};

/**
 * Dashboard Statistics Mock Data
 */
export const mockDashboardStats = {
  totalCandidates: 125,
  activeInterviews: 8,
  completedInterviews: 45,
  pendingInterviews: 12,
  averageScore: 78.5,
  highRiskCandidates: 3
};

/**
 * Recent Activity Mock Data
 */
export const mockRecentActivity = [
  {
    type: 'interview_completed',
    description: 'John Doe completed Software Engineer interview',
    timestamp: '2024-01-15T10:30:00Z',
    candidateName: 'John Doe',
    jobTitle: 'Software Engineer'
  },
  {
    type: 'candidate_added',
    description: 'New candidate Jane Smith added to system',
    timestamp: '2024-01-15T09:15:00Z',
    candidateName: 'Jane Smith'
  },
  {
    type: 'interview_created',
    description: 'Interview created for Bob Wilson - Accountant position',
    timestamp: '2024-01-15T08:45:00Z',
    candidateName: 'Bob Wilson',
    jobTitle: 'Accountant'
  },
  {
    type: 'high_risk_flagged',
    description: 'High risk candidate flagged: Alice Johnson',
    timestamp: '2024-01-14T16:20:00Z',
    candidateName: 'Alice Johnson',
    riskLevel: 'high'
  },
  {
    type: 'interview_started',
    description: 'Carol Brown started HR Specialist interview',
    timestamp: '2024-01-14T14:10:00Z',
    candidateName: 'Carol Brown',
    jobTitle: 'HR Specialist'
  }
];

/**
 * Chart Data Mock
 */
export const mockChartData = {
  interviewTrends: {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
      {
        label: 'Completed',
        data: [12, 15, 18, 22],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)'
      },
      {
        label: 'Started',
        data: [15, 18, 21, 25],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)'
      }
    ]
  },
  riskDistribution: {
    labels: ['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk'],
    datasets: [
      {
        data: [65, 25, 8, 2],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(249, 115, 22, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ]
      }
    ]
  },
  scoreHistogram: {
    labels: ['0-20', '21-40', '41-60', '61-80', '81-100'],
    datasets: [
      {
        label: 'Candidates',
        data: [2, 8, 15, 35, 25],
        backgroundColor: 'rgba(99, 102, 241, 0.8)'
      }
    ]
  }
};

/**
 * Utility functions for test data
 */
export const testDataUtils = {
  /**
   * Generate random test candidate
   */
  generateRandomCandidate(): TestCandidate {
    const firstNames = ['Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Riley', 'Avery', 'Quinn'];
    const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'];
    
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@test.com`;
    const phone = `+1${Math.floor(Math.random() * 9000000000) + 1000000000}`;
    
    return { firstName, lastName, email, phone };
  },

  /**
   * Generate unique pass key
   */
  generatePassKey(): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < 8; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  },

  /**
   * Generate test email with timestamp
   */
  generateUniqueEmail(prefix: string = 'test'): string {
    const timestamp = Date.now();
    return `${prefix}.${timestamp}@test.com`;
  },

  /**
   * Create batch of test candidates
   */
  createCandidateBatch(count: number): TestCandidate[] {
    const candidates: TestCandidate[] = [];
    for (let i = 0; i < count; i++) {
      candidates.push(this.generateRandomCandidate());
    }
    return candidates;
  }
};
