# Pump Express Test Fields Specification

For TenJI test script generation targeting MediaTek PE protocol validation.

## Protocol Type
- PE 1.0/2.0: VBUS Current Pulsing (Load Modulation)
- PE 3.0: CC signaling
- PE 4.0: USB PD 3.0 PPS compatible

## Required Test Fields for TenJI

### 1. Connection & Initial State
- `pe_attach`: Verify standard 5V VBUS state is established before pulsing begins.

### 2. Load Modulation (PE 1.0 / 2.0)
- `pe_current_pulse_inject`: Instruct programmable load to draw specific current pulse patterns.
  - Parameter: `pulse_width_ms`, `pulse_amplitude_ma`.
- `pe_voltage_step_up`: Verify sequential voltage stepping (e.g., 5V -> 7V -> 9V -> 12V). Note: Protocol requires sequential steps; skipping is not allowed.
- `pe_timeout_long`: Must override standard timeouts. A full sweep 5V->12V can take up to ~2.1 seconds. Timeout set to 3000ms minimum.

### 3. State & Fallback
- `pe_pulse_decode_fail`: Inject malformed pulses and verify Source ignores them and maintains current voltage or falls back safely to 5V.
