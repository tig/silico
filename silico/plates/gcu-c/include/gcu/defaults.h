#ifndef GCU_DEFAULTS_H
#define GCU_DEFAULTS_H

/* Shipped product defaults — metal and host tests share this table. */

#define GCU_TICK_SLEEP_MS 250

typedef struct {
  int tick_sleep_ms;
} gcu_defaults_t;

/* Single shipped table (product path must use this, not parallel literals). */
extern const gcu_defaults_t GCU_DEFAULTS;

#endif
