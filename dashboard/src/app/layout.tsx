import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
    title: 'GitHub AI Repository Analytics',
    description: 'Analytics dashboard for GitHub AI/ML repositories',
    keywords: ['github', 'analytics', 'ai', 'machine-learning', 'repositories', 'data-science'],
    authors: [{ name: 'GitHub AI Analytics' }],
    openGraph: {
        title: 'GitHub AI Repository Analytics',
        description: 'Analytics dashboard for GitHub AI/ML repositories',
        type: 'website',
    },
}

export const viewport: Viewport = {
    themeColor: [
        { media: '(prefers-color-scheme: light)', color: '#ffffff' },
        { media: '(prefers-color-scheme: dark)', color: '#0f172a' },
    ],
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className={`${inter.variable} font-sans antialiased`}>
                {children}
            </body>
        </html>
    )
}