import { ImageResponse } from 'next/og';

export const runtime = 'edge';
export const alt = 'InfraCostIQ cloud infrastructure cost intelligence';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        padding: '72px',
        background: '#0b1220',
        color: '#f8fafc',
        fontFamily: 'Arial, sans-serif',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '48px' }}>
          <div style={{
            width: '190px',
            height: '190px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#10c98b',
            transform: 'rotate(45deg)',
            color: '#ffffff',
            fontSize: '66px',
            fontWeight: 700,
          }}>
            <span style={{ transform: 'rotate(-45deg)' }}>IQ</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
            <div style={{ fontSize: '68px', fontWeight: 700 }}>InfraCostIQ</div>
            <div style={{ fontSize: '30px', color: '#b7c4d6' }}>Cloud infrastructure cost intelligence</div>
            <div style={{ fontSize: '23px', color: '#55dfad' }}>AWS · Azure · Google Cloud · Kubernetes · On-prem</div>
          </div>
        </div>
      </div>
    ),
    { ...size },
  );
}