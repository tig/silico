#ifndef GCU_HAL_H
#define GCU_HAL_H

/* Portable HAL contract — no device headers here. */

typedef struct gcu_hal gcu_hal_t;

struct gcu_hal {
  void (*set_led)(gcu_hal_t *self, int on);
  void (*delay_ms)(gcu_hal_t *self, int ms);
};

#endif
