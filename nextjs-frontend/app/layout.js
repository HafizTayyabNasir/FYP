import './globals.css';
import AppShell from './components/AppShell';
import { ToastProvider } from './components/ToastProvider';

export const metadata = {
  title: 'AI Client Hunt & Outreach',
  description: 'AI-powered system for hunting potential clients and automated outreach',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
        <script dangerouslySetInnerHTML={{
          __html: `
            try {
              var theme = localStorage.getItem('theme');
              if (theme === 'light') {
                document.documentElement.classList.remove('dark');
              } else {
                document.documentElement.classList.add('dark');
              }
            } catch (_) {}
          `
        }} />
      </head>
      <body className="bg-[#F8FAFC] dark:bg-[#08061a] min-h-screen text-slate-600 dark:text-[#c8c4e8] font-medium selection:bg-[#6D5DF6]/30 transition-colors duration-300" suppressHydrationWarning>
        <ToastProvider>
          <AppShell>{children}</AppShell>
        </ToastProvider>
      </body>
    </html>
  );
}
