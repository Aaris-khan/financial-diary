const CACHE_NAME = 'aarish-dairy-shell-v1';

self.addEventListener('install', function() {
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    const targetUrl = new URL((event.notification.data && event.notification.data.url) || './', self.registration.scope).href;
    event.waitUntil((async function() {
        const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
        for (const client of clients) {
            if ('focus' in client) {
                try { await client.focus(); } catch (e) {}
                try { if ('navigate' in client) await client.navigate(targetUrl); } catch (e) {}
                return;
            }
        }
        if (self.clients.openWindow) await self.clients.openWindow(targetUrl);
    })());
});
