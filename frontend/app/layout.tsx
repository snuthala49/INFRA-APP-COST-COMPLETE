import '../styles/globals.css';
import type { Metadata } from 'next';

const siteUrl = new URL('https://www.infracostiq.com');
const googleVerification = process.env.GOOGLE_SITE_VERIFICATION;
const bingVerification = process.env.BING_SITE_VERIFICATION;

export const metadata: Metadata = {
  metadataBase: siteUrl,
  title: {
    default: 'InfraCostIQ | Cloud Infrastructure Cost Estimator',
    template: '%s | InfraCostIQ',
  },
  description: 'Compare AWS, Azure, Google Cloud, Kubernetes, and on-prem infrastructure costs with transparent pricing assumptions and database estimates.',
  applicationName: 'InfraCostIQ',
  alternates: {
    canonical: '/',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
    },
  },
  openGraph: {
    type: 'website',
    url: '/',
    siteName: 'InfraCostIQ',
    locale: 'en_US',
    title: 'InfraCostIQ | Cloud Infrastructure Cost Estimator',
    description: 'Compare infrastructure costs across AWS, Azure, Google Cloud, Kubernetes, and on-prem with transparent assumptions.',
    images: [{ url: 'https://www.infracostiq.com/opengraph-image', width: 1200, height: 630, alt: 'InfraCostIQ cloud cost intelligence' }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'InfraCostIQ | Cloud Infrastructure Cost Estimator',
    description: 'Compare infrastructure costs across AWS, Azure, Google Cloud, Kubernetes, and on-prem.',
    images: ['https://www.infracostiq.com/opengraph-image'],
  },
  verification: {
    ...(googleVerification ? { google: googleVerification } : {}),
    ...(bingVerification ? { other: { 'msvalidate.01': bingVerification } } : {}),
  },
};

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
