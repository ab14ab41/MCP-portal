import { Boxes } from 'lucide-react';
import { ThemeToggle } from '@/components/ui/theme-toggle';

function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center shadow-sm">
            <Boxes className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-semibold tracking-tight">MCP Portal</span>
        </div>
        <nav className="hidden md:flex items-center gap-8">
          <a href="/" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
            Projects
          </a>
          <a href="/deployed-mcps" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Deployment
          </a>
          <a href="/ai-testing" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            AI Sandbox
          </a>
          <a href="/documentation" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
            Documentation
          </a>
        </nav>
        <div className="flex items-center gap-4">
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}

export default Header;
