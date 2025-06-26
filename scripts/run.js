#!/usr/bin/env node
import path from 'path';
import { spawn } from 'child_process';
import inquirer from 'inquirer';
import dotenv from 'dotenv';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables from .env if present
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  dotenv.config({ path: envPath });
}

const SCRIPTS = {
  'mongodb-clean': {
    description: 'Cleanup old documents from MongoDB collections',
    script: path.join(__dirname, 'mongodb-clean', 'clean.js'),
    params: {
      MONGO_URI: { message: 'Mongo connection URI' },
      DATE_CUTOFF: { message: 'Cutoff date (YYYY-MM-DD)' },
      BATCH_SIZE: { message: 'Batch size', default: '100' },
      DELAY_MS: { message: 'Delay between batches (ms)', default: '200' },
      N_BATCH_CHECKPOINT: { message: 'Batch checkpoint interval', default: '5000' }
    }
  }
};

async function main() {
  const choices = Object.keys(SCRIPTS).map((key) => ({
    name: `${key} - ${SCRIPTS[key].description}`,
    value: key
  }));

  const { chosen } = await inquirer.prompt([
    {
      type: 'list',
      name: 'chosen',
      message: 'Select a script to run',
      choices
    }
  ]);

  const scriptInfo = SCRIPTS[chosen];
  const prompts = [];

  for (const [envVar, meta] of Object.entries(scriptInfo.params)) {
    const defaultVal = process.env[envVar] || meta.default || '';
    prompts.push({
      type: 'input',
      name: envVar,
      message: meta.message || envVar,
      default: defaultVal
    });
  }

  const answers = await inquirer.prompt(prompts);
  const env = { ...process.env, ...answers };

  const child = spawn('node', [scriptInfo.script], {
    stdio: 'inherit',
    env
  });

  child.on('exit', (code) => {
    console.log(`Script exited with code ${code}`);
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
