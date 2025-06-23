import express from 'express';
import path    from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);
const app        = express();

// ─── 1) Serve everything under “public/” at the web root ──────────────
app.use(express.static(path.join(__dirname, 'public')));

// (Optional) If you want “/” to serve your index.html automatically:
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ─── 2) Endpoint to start the Broker EXE ────────────────────────────
app.post('/start-broker', (req, res) => {
  console.log('▶️  Received POST /start-broker');

  // Absolute path to your EXE; this lives in “../AOS Server/dist/...”
  const exePath = path.join(
    __dirname,       // e.g. …/AOS Waypoint planning-Test
    '..',            // goes up to …/AOS Ground Station New
    'AOS Server',
    'AOS_Broker.exe'
  );

  // Set cwd = AOS Ground Station New (so any relative folder creations by the EXE
  // will happen under …/AOS Ground Station New instead of …/AOS Waypoint planning-Test)
  const runOptions = {
    cwd: path.join(__dirname, '..'),
    detached: false,
    stdio: ['ignore', 'inherit', 'inherit'],
    windowsHide: false
  };

  console.log(`🔧 Spawning EXE: ${exePath}`);
  const child = spawn(exePath, [], runOptions);
  console.log(`🐣 Spawned broker EXE with PID ${child.pid}`);

  res.json({ message: 'Broker EXE launched (with cwd set to parent folder)' });
});

// ─── 3) Launch the Node app ─────────────────────────────────────────
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Launcher listening at http://localhost:${PORT}`);
});
