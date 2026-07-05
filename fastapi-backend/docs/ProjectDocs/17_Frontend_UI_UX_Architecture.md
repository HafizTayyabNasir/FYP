# 17 — Frontend UI/UX Architecture (Next.js & React)

## 17.1 Modern App Router Architecture
The frontend utilizes the Next.js 14 App Router (`app/` directory) to enable Server-Side Rendering (SSR) and optimized Client-Side Routing.
- **Layouts**: `layout.js` manages the global theme and state providers.
- **Shell Patterns**: `AppShell` and `PublicShell` dynamically render sidebars and navbars based on authentication state, avoiding redundant DOM renders.

## 17.2 Premium Design Aesthetics
To meet modern SaaS standards, the UI employs:
- **Tailwind CSS**: For utility-first, responsive styling.
- **Framer Motion**: For complex micro-interactions, page transitions, and staggered list animations (e.g., Dashboard metrics rendering).
- **Glassmorphism**: Backdrop blurring and semi-transparent layers create a depth-of-field effect in the `AppShell`.
- **Theme Management**: Native Dark/Light mode switching persisting via `localStorage` and synchronized with Tailwind's `dark:` classes.

## 17.3 State Management & Auth Flow
- **useSyncExternalStore**: Used to subscribe React components to `localStorage` changes, ensuring multi-tab authentication synchronization.
- **JWT Persistence**: Access tokens are stored locally and attached to the `Authorization: Bearer <token>` header for all authenticated outbound requests.
- **Hydration Safety**: Theme toggling injects a blocking script in `<head>` to prevent Flash of Unstyled Content (FOUC) and React hydration mismatches.

## 17.4 Advanced Components
- **Rich Text Editor**: A custom WYSIWYG editor built for the Outreach generator, allowing users to format text (Bold, Italic, Alignment, Colors) before dispatching SMTP emails.
- **Dynamic Dashboards**: Real-time metric calculation components based on the user's historical campaign and audit data.
