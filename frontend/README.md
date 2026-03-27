# Frontend - Next.js React Application

This directory contains the Next.js React frontend application for the Varivilambarangal project.

## Tech Stack

- **Framework**: Next.js 16.1.1
- **React**: 19.2.3
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Linting**: ESLint

## Project Structure

```
frontend/
├── src/                    # Source code
│   ├── app/               # Next.js app router
│   ├── lib/               # Utility libraries
│   └── ...
├── public/                # Static assets
├── package.json           # Dependencies and scripts
├── next.config.js         # Next.js configuration
├── tsconfig.json          # TypeScript configuration
├── eslint.config.mjs      # ESLint configuration
├── postcss.config.mjs     # PostCSS configuration
└── next-env.d.ts          # Next.js TypeScript declarations
```

## Getting Started

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Build for production**:
   ```bash
   npm run build
   ```

4. **Start production server**:
   ```bash
   npm run start
   ```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## API Integration

The frontend communicates with the Django backend API located in `../backend/`.

- **API Base URL**: `http://localhost:8000/api/v1/`
- **Admin Interface**: `http://localhost:8000/employee/`