import '../styles/globals.css';

export const metadata = {
  title: 'InfraCostIQ',
  description: 'Estimate and compare infrastructure costs across hosting platforms',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        {/* Use Inter + JetBrains Mono for a modern, technical look */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:ital,wght@0,400;0,700&display=swap" rel="stylesheet" />
      </head>
      <body className="min-h-screen font-sans bg-[#0B1220] text-slate-100">
        <main>{children}</main>
      </body>
    </html>
  )
}
