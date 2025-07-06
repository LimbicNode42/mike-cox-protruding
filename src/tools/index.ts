/**
 * Database Tools Exports
 *
 * This file provides a centralized export for all database tool functions.
 */

import { registerPostgresTools } from './postgres.js';
import { registerRedisTools } from './redis.js';
import { registerMongoTools } from './mongodb.js';
import { registerInfluxTools } from './influxdb.js';

export { registerPostgresTools, registerRedisTools, registerMongoTools, registerInfluxTools };

export default {
  registerPostgresTools,
  registerRedisTools,
  registerMongoTools,
  registerInfluxTools,
};
