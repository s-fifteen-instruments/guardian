/* vim: set ts=2 sw=2 tw=0 et nowrap :*/
/*
 * Guardian is a quantum key distribution REST API and supporting software stack.
 * Copyright (C) 2021  W. Cyrus Proctor
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 *
*/

/* Exposes clock_gettime and
 * clock_nanosleep feature test macros */
#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200112L
#endif
/* Wraps "expensive" calls that are
 * meant to help with debugging only. */
#ifndef DEBUG
#define DEBUG 0
#endif
/* Borrowed from stdint.h for PRIu64 */
#ifndef __STDC_FORMAT_MACROS
#define __STDC_FORMAT_MACROS
#endif

#include "pcg.h"
#include <errno.h>
#include <getopt.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <signal.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>

/* Macro for uint64_t printing */
#define EF PRIu64
/* Make basic maximum/minimum functions;
 * keep x and y primitive */
#define MAX(x, y) (((x) < (y)) ? (y) : (x))
#define MIN(x, y) (((x) < (y)) ? (x) : (y))
/* TCONV, T2NS, TUNIT, AND TSUNIT macros are interdependent:
 * For example, choose time units in nanoseconds:
 *   TCONV = 1E9
 *   T2NS = 1
 *   TUNIT = "[ns]"
 *   TSUNIT = 8
 * If one chose microseconds instead:
 *   TCONV = 1E6
 *   T2NS = 1000
 *   TUNIT = "[us]"
 *   TSUNIT = 8000
 */
/* Time conversion from seconds to simulation time unit
 * used throughout the code. NOTE: Take care that TCONV
 * does not get too big (>1E9) to preserve signficant
 * digits for Epoch numbers (current at 64-bits) */
#define TCONV (Epoch)1E9
/* Unit conversion from simulation time unit to nanoseconds */
#define T2NS (Epoch)1
/* Time unit to display in output */
#define TUNIT "[ns]"
/* Conversion from simulation time unit to multiples
 * of timestamp unit time => 1/125 picoseconds. */
#define TSUNIT (Epoch)8
/* Typecast Integer Literals */
#define ZERO (Epoch)0
#define ONE (Epoch)1
/* Natural Log */
#define ln(x) log(x)
/* Log Function Macros */
#define C(...) logif("CRITICAL", __VA_ARGS__)
#define E(...) logif("ERROR", __VA_ARGS__)
#define W(...) logif("WARN", __VA_ARGS__)
#define I(...) logif("INFO", __VA_ARGS__)
#define D(...) logif("DEBUG", __VA_ARGS__)
/* Binary Printing */
#define B(...) bprintf(__VA_ARGS__)

/* -------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------- */

/* Rawevent type */
typedef uint32_t RE;
/* Epoch type */
typedef uint64_t Epoch;
/* Rawevent struct for 64-bit wide timestampper events */
struct rawevent {
  RE cv;
  RE dv;
};
/* A pair of detector states */
struct detstatepair {
  Epoch hec_state;
  Epoch lec_state;
  bool match;
};
/* Toggle to indicate the program has caught
 * a signal volatile keyword important. */
volatile bool interrupted = (bool)false;
#if DEBUG
/* Everyone needs a spinner; shows
 * event simulation progress. */
char *spinner[] = {
    "/",
    "-",
    "\\",
    "|",
};
static int spindex = 0;
#endif
/* Log levels */
enum log_level { LOFF, LCRITICAL, LERROR, LWARN, LINFO, LDEBUG, LBINARY };
/* Global Log Level */
static int verbosity = LINFO;

/* -------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------- */
/* Function Declarations */

static inline void logif(const char *log_tag, FILE *stream, const char *fmt,
                         ...);
/* static inline Epoch microseconds_since_epoch(FILE *stream); */
static inline Epoch nanoseconds_since_epoch(FILE *stream);
#if DEBUG
static inline void bin(FILE *stream, Epoch num, Epoch index);
static inline void bprintf(FILE *stream, const char *message, Epoch value,
                           bool print_header);
#endif
static inline bool uniform_boolean(void);
static inline Epoch uniform_epoch(Epoch A);
static inline double uniform_double();
static inline double quantile_exp(double lambda);
static inline struct detstatepair
generate_detector_state_pair(const Epoch hec2lec_det_map[],
                             const Epoch det_map_uncorrelated[],
                             double det_state_error_fraction);
static inline Epoch clock_skew(Epoch offset, double frequency_diff, Epoch t);
static inline bool check_photon_loss(double loss_fraction);
static inline bool get_entropy(void *dest, size_t size);
static inline void signal_handler(int a_signal);
static inline void display_usage(FILE *log_fh, char *argv[]);

/* -------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------- */

static inline void logif(const char *log_tag, FILE *stream, const char *fmt,
                         ...) {
  /*
   *  Function to print and tag a particular log message only if the
   *  current global verbosity level is high enough to merit the message
   *  to be printed to the passed-in file stream. Critical messages are
   *  printed regardless. The file stream is assumed to already be open.
   *  The fmt and var args allow the call to contain fprintf-like formatting.
   *
   *  Arguments:
   *  (const char *) log_tag - expected to be either "CRITICAL", "ERROR",
   *                           "WARN", "INFO", or "DEBUG". Used to
   *                           distinguish when and what to print.
   *  (FILE *) stream - already open file stream to print the message to.
   *  (const char*) fmt - formatting for additional parameters to be passed
   *                      on to vfprintf
   *
   *  Returns Values:
   *  None
   */
  va_list args;
  if (strncmp(log_tag, "CRITICAL", (size_t)7) == (int)0) {
    /* log regardless; no nested if statement here */
    fprintf(stream, "[%s] ", log_tag);
    va_start(args, fmt);
    vfprintf(stream, fmt, args);
    va_end(args);
  } else if (strncmp(log_tag, "ERROR", (size_t)5) == (int)0) {
    if (verbosity >= LERROR) {
      fprintf(stream, "[%s] ", log_tag);
      va_start(args, fmt);
      vfprintf(stream, fmt, args);
      va_end(args);
    }
  } else if (strncmp(log_tag, "WARN", (size_t)4) == (int)0) {
    if (verbosity >= LWARN) {
      fprintf(stream, "[%s] ", log_tag);
      va_start(args, fmt);
      vfprintf(stream, fmt, args);
      va_end(args);
    }
  } else if (strncmp(log_tag, "INFO", (size_t)4) == (int)0) {
    if (verbosity >= LINFO) {
      fprintf(stream, "[%s] ", log_tag);
      va_start(args, fmt);
      vfprintf(stream, fmt, args);
      va_end(args);
    }
  } else if (strncmp(log_tag, "DEBUG", (size_t)5) == (int)0) {
    if (verbosity >= LDEBUG) {
      fprintf(stream, "[%s] ", log_tag);
      va_start(args, fmt);
      vfprintf(stream, fmt, args);
      va_end(args);
    }
  }
}

/* -------------------------------------------------------------------------- */

#if 0
static inline Epoch microseconds_since_epoch(FILE *stream) {
  /*
   * Using gettimeofday, Return an Epoch number filled with the number of
   * microseconds since the Unix epoch time 00:00:00 UTC on 1 January 1970.
   *
   * Arguments:
   * None
   *
   * Return Values:
   * (Epoch) - number of microseconds since unix epoch
   */

  struct timeval tv;
  Epoch microseconds_since_epoch = ZERO;

  /* Get time of day accurate down to the microsecond. */
  if (gettimeofday(&tv, NULL) != (int)0) {
    C(stream, "%s: gettimeofday() failed, errno = %d\n", __func__, errno);
  }

  microseconds_since_epoch = (Epoch)tv.tv_sec * (Epoch)1E6 + (Epoch)tv.tv_usec;

  return microseconds_since_epoch;
}
#endif

/* -------------------------------------------------------------------------- */

static inline Epoch nanoseconds_since_epoch(FILE *stream) {
  /*
   * Using clock_gettime, Return an Epoch number filled with the number of
   * nanoseconds since the Unix epoch time 00:00:00 UTC on 1 January 1970.
   *
   * Arguments:
   * None
   *
   * Return Values:
   * (Epoch) - number of nanoseconds since unix epoch
   */

  struct timespec ts;
  Epoch nanoseconds_since_epoch = ZERO;

  /* Get time including nanoseconds since epoch */
  if (clock_gettime(CLOCK_REALTIME, &ts) != (int)0) {
    C(stream, "%s: clock_gettime() failed, errno = %d\n", __func__, errno);
  }

  nanoseconds_since_epoch = (Epoch)ts.tv_sec * (Epoch)1E9 + (Epoch)ts.tv_nsec;

  return nanoseconds_since_epoch;
}

/* -------------------------------------------------------------------------- */

#if DEBUG
static inline void bin(FILE *stream, Epoch num, Epoch index) {
  /*
   * Give a value and number of bit, display it in binary form using recursion.
   *
   * Arguments:
   * value (Epoch) - value to print in binary
   * index (Epoch) - size index of value
   *
   * Return Values:
   * None
   */

  if (index > ZERO) {
    bin(stream, num / (Epoch)2, index - (Epoch)1);
    fprintf(stream, "%" EF, num % 2);
  }
}

/* -------------------------------------------------------------------------- */

static inline void bprintf(FILE *stream, const char *message, Epoch value,
                           bool print_header) {
  /*
   * Basic printing of a message and binary form of an Epoch number.
   *
   * Arguments:
   * stream (FILE*) - open file handle to write to
   * message (const char*) - Message to print
   * value (Epoch) - value to display in binary
   *
   * Return Values:
   * None
   */

  if (verbosity >= LBINARY) {
    Epoch num_size = sizeof(value) * CHAR_BIT;
    if (print_header) {
      Epoch i = 0;
      /* Pad with spaces the width of the message + 9 for BINARY */
      fprintf(stream, "%*s", (int)strlen(message) + 9, "");
      for (i = 0; i < num_size; ++i) {
        fprintf(stream, "%" EF, i % (Epoch)10);
      }
      fprintf(stream, "\n");
    }
    fprintf(stream, "[BINARY] %s", message);
    bin(stream, value, num_size);
    fprintf(stream, "\n");
  }
}
#endif /* DEBUG */

/* -------------------------------------------------------------------------- */

static inline bool uniform_boolean(void) {
  /*
   * Provide a uniformly distributely function that returns true or false.
   * This assumes that uniform_epoch will return [0, 2) ==> 0 or 1 uniformly.
   * This result is then type cast to a boolean.
   *
   * Arguments:
   * None
   *
   * Return Values:
   * (bool) random uniform bool
   */

  return (bool)uniform_epoch((Epoch)2);
}

/* -------------------------------------------------------------------------- */

static inline Epoch uniform_epoch(Epoch A) {
  /*
   * Provide a random Epoch (integer-based) between [0, A)
   * Generates a uniformly distributed 32-bit unsigned integer
   * less than bound (i.e., x where 0 <= x < A).
   * Some programmers may think that they can just run
   * pcg32_random() % A, but doing so introduces nonuniformity
   * when bound is not a power of two. The code for
   * pcg32_boundedrand avoids the nonuniformity by dropping a
   * portion of the RNG's output.
   *
   * NOTE: Originally coded for "small" values of A; i.e. A < UINT32_MAX.
   *
   * Arguments:
   * A (Epoch) - upper end of the range for the random Epoch number
   *
   * Return Values:
   * (Epoch) - random Epoch number between 0 inclusive and A exclusive
   */

  return (Epoch)pcg32_boundedrand((uint32_t)A);
}

/* -------------------------------------------------------------------------- */

static inline double uniform_double(void) {
  /*
   * Provide a random double [0, 1)
   * https://www.pcg-random.org/using-pcg-c-basic.html
   * If you are happy to have a floating point value in the range
   * [0,1) that has been rounded down to the nearest multiple of
   * 1/23**2, you can use this function.
   *
   * Arguments:
   * None
   *
   * Return Values:
   * (double) - random variable between 0 include and 1 exclusive
   */

  return ldexp(pcg32_random(), -32);
}

/* -------------------------------------------------------------------------- */

static inline double quantile_exp(double lambda) {
  /*
   * Evaluate a Poisson type event from the inverse cumulative distribution
   * function, AKA Poisson quantile function.
   * https://en.wikipedia.org/wiki/Quantile_function
   * lambda: rate lambda = 1/mean
   * uniform_random returns a uniformly distributed random float [0, 1).
   * Xi ==> make sure to never take ln(0)
   *
   * Arguments:
   * lambda (double) - 1/mean of the distribution; e.g. could be a rate (for
   * time) or inverse distance; must be > 0
   *
   * Return Values:
   * (double) - value of the random variable such that the probability of the
   *           variable being less than or equal to that value equals the given
   *           probability
   */

  double Xi = (double)0;
  double quantile_exp = (double)0;
  double random_number = (double)0;
  /* Sample a uniformly distributed random double [0, 1) */
  random_number = uniform_double();
  /* Ensures that Xi will never be 0 */
  Xi = (double)1.0 - random_number;
  /* This can safely be sampled for any value of Xi */
  /* lamdba can never be 0 either */
  quantile_exp = -ln(Xi) / lambda;

#if DEBUG
  /* printf("%f %f %f %f", random_number, Xi, lambda, quantile_exp); */
#endif

  return quantile_exp;
}

/* -------------------------------------------------------------------------- */

static inline struct detstatepair
generate_detector_state_pair(const Epoch det_map_correlated[],
                             const Epoch det_map_uncorrelated[],
                             double det_state_error_fraction) {
  /*
   * Generate HEC and LEC detector states that are either matching
   * or independent and randomly generated. HEC first chooses a detector
   * state (1, 2, 4, or 8). Then, a random number is sampled to see if the
   * LEC party measures in the same polarization basis. If so, then the
   * LEC detector state is correctly mapped to be equivalent to the chosen
   * HEC detector state. If the LEC basis measurement is chosen not to match,
   * then the remaining two detectors will be 50/50 sampled to click (i.e no
   * correlation). In the case of a matching basis measurement, error can be
   * introduced by a det_state_error_fraction. This fraction should correspond
   * to introducing a controllable source of error into the signal which will
   * later be picked up as a non-zero QBER.
   *
   * Detector state mapping from HEC party to LEC party
   *     1 2 4 8 (detector click 0001 0010 0100 1000)
   * HEC V - H +
   * LEC H + V -
   * qcrypto default => 4 8 1 2
   *
   * NOTE: Indexed mapping creates a non-uniform stride when doing lookups
   *       leading to a potential performance penalty.
   *
   * Arguments:
   * det_state_error_fraction (double) - >=0 and <=1; Probability of generating
   *   non-matching states when measurement bases match
   *
   * Return Values:
   * ds_pair (detstatepair) - Pair of Epoch numbers w/ HEC & LEC detector states
   *   along with a true match flag.
   */

  struct detstatepair ds_pair = {ZERO, ZERO, false};
  bool matching_basis = false;
  bool det_choice = false;
  bool gen_match = false;
  Epoch hec_random_epoch = ZERO;
  double random_double = (double)0;

  /* Pick a result for the HEC party */
  /* Provide random number 0, 1, 2, or 3 */
  /* Produce either 1*2**0 = 1 (0001),
   *                1*2**1 = 2 (0010),
   *                1*2**2 = 4 (0100),
   *             or 1*2**3 = 8 (1000)
   * Use left bit shift operator to achieve this
   * Range of uniform_epoch is [0,A) */
  hec_random_epoch = uniform_epoch((Epoch)4);
  ds_pair.hec_state = ONE << hec_random_epoch;

  /* Randomly sample to determine if LEC party will */
  /* measure in the same basis or not; 50/50 chance. */
  matching_basis = uniform_boolean();

  /* HEC and LEC parties measure in the same basis */
  if (matching_basis) {
    /* Sample to determine if we generate a true correlated detector match
     * or if we introduce an uncorrelated error into the signal. */
    random_double = uniform_double();
    gen_match = random_double > det_state_error_fraction;
    /* Choose the correlated detector of the matching basis for LEC */
    if (gen_match) {
      /* hec_random_epoch must be 0, 1, 2 or 3 */
      ds_pair.lec_state = det_map_correlated[(size_t)hec_random_epoch];
      ds_pair.match = true;
      /* Choose the uncorrelated detector of the matching basis for LEC */
    } else {
      /* hec_random_epoch must be 0, 1, 2 or 3 */
      ds_pair.lec_state = det_map_uncorrelated[(size_t)hec_random_epoch];
    }
  }
  /* LEC party does not measure in the same basis */
  else {
    /* Randomly sample to see which detector will be */
    /* chosen; 50/50 chance. */
    det_choice = uniform_boolean();
    /* HEC party chose a 1 or 4; maps to V or H by default */
    if (ds_pair.hec_state == (Epoch)1 || ds_pair.hec_state == (Epoch)4) {
      /* LEC must choose non-matching detector click; i.e. + or - */
      if (det_choice) {
        ds_pair.lec_state = det_map_correlated[(size_t)1]; /* default: 2 */
      } else {
        ds_pair.lec_state = det_map_correlated[(size_t)3]; /* default: 8 */
      }
      /* HEC party chose a 2 or 8; maps to - or + by default */
    } else {
      /* else if (ds_pair.hec_state == (Epoch)2 || ds_pair.hec_state ==
       * (Epoch)8) { */
      /* LEC must choose non-matching detector click; i.e. H or V */
      if (det_choice) {
        ds_pair.lec_state = det_map_correlated[(size_t)0]; /* default: 1 */
      } else {
        ds_pair.lec_state = det_map_correlated[(size_t)2]; /* default: 4 */
      }
    }
  }

  return ds_pair;
}

/* -------------------------------------------------------------------------- */

static inline Epoch clock_skew(Epoch offset, double frequency_diff, Epoch t) {
  /*
   * Given a time offset and a clock frequency difference, return a linear
   * time skew with constant time offset. This mimics what is measured and
   * reported in DSTA Report 3 given Rubidium reference clocks. Make sure to
   * match units correctly across arguments.
   *
   * Arguments:
   * offset (Epoch) - constant time offset
   * frequency_diff (double) - frequency difference between the two clocks
   * t (Epoch) - time
   *
   * Return Values:
   * (Epoch) - clock skew at time t given frequency_diff and constant offset
   */

  /* Only allocated at beginning of program */
  static double frequency_drift_dbl = (double)0;
  static Epoch frequency_drift_Eph = ZERO;

  /* The double will collect drift over multiple function calls */
  frequency_drift_dbl += (double)(frequency_diff * t);
  frequency_drift_Eph = (Epoch)frequency_drift_dbl;

  /* If the frequency drift becomes large enough to register in an
   * Epoch variable, then the double variable is decremented appropriately */
  if (frequency_drift_Eph > ZERO) {
    frequency_drift_dbl -= (double)frequency_drift_Eph;
  }

  return (Epoch)frequency_drift_Eph + (Epoch)offset;
}

/* -------------------------------------------------------------------------- */

static inline bool check_photon_loss(double loss_fraction) {
  /*
   * Given a loss fraction between 0 and 1, evaluate a uniform
   * random number between [0, 1)  to see if this photon should be
   * propagated or destroyed. This is a Russian Roulette Monte Carlo
   * technique.
   *
   * Arguments:
   * loss_fraction (double) - 0 => no probability of loss;
   *                          1 => all probability loss
   *
   * Return Values:
   * (bool) - true => photon propagated; false => photon destroyed
   *
   */

  bool propagate_photon = (bool)true;
  double random_number = (double)0;
  random_number = uniform_double();
  if (random_number <= loss_fraction) {
    propagate_photon = false;
  }

  return propagate_photon;
}

/* -------------------------------------------------------------------------- */

static inline bool get_entropy(void *dest, size_t size) {
  /*
   * Given some memory destination, *dest, and the size of this memory, size,
   * attempt to open a source of randomness from the kernel's RNG, and fill
   * it. Note that /dev/urandom is an unaccepable cryptographic source of
   * randomness. This function is to be used with this in mind.
   * https://linux.die.net/man/4/urandom
   *
   * Arguments:
   * (void *) dest - memory location to write random bytes to.
   * (size_t) size - size of the memory location in bytes
   *
   * Returns:
   * (bool) - true if operation was succesful; false otherwise
   */
  /* Presumes we're on UNIX-like machine */
  FILE *fh = fopen("/dev/urandom", "r");
  /* Bail if file handle isn't valid */
  if (fh < 0) {
    return false;
  }
  /* Read size bytes from fh and put it in dest */
  ssize_t sz = fread(dest, size, 1, fh);
  /* Make size is right and we can successfully close fh */
  return (fclose(fh) == 0) && (sz == (ssize_t)size);
}

/* -------------------------------------------------------------------------- */

static inline void signal_handler(int a_signal) {
  /*
   * Given a signal, close up gracefully by setting the global volatile
   * variable interrupted to true.
   *
   * Arguments:
   * a_signal (int) - caught signal to handle
   *
   * Return values:
   * None
   */

  switch (a_signal) {
  case SIGINT:
    fprintf(stderr, "\n\nCaught SIGINT: closing gracefully...\n\n");
    fflush(stderr);
    interrupted = true;
    break;
  case SIGTERM:
    fprintf(stderr, "\n\nCaught SIGTERM: closing gracefully...\n\n");
    fflush(stderr);
    interrupted = true;
    break;
  }
}

/* -------------------------------------------------------------------------- */

static inline void display_usage(FILE *log_fh, char *argv[]) {
  /*
   * Display usage information about this program.
   *
   * Arguments:
   * log_fh (FILE*) - open filehandle for logging usage information
   * argv (char*[]) - array of char* filled with command-line arguments
   *
   * Return Values:
   * None
   */
  I(log_fh, "\n");
  I(log_fh, "Usage for %s:\n", argv[0]);
  I(log_fh, "\n");
  I(log_fh, "    %s \\\n", argv[0]);
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-h] /* Display This Help Message And Quit */ \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-v] /* Increase Verbosity By One */ \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-q] /* Decrease Verbosity By One */ \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-i] /* Run Indefinitely Until Signal */ \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-r] /* Reproducible Initial Time & RNG Sequence */ \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-u] /* Simulate Uniform Time Between Photon Events */ \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-R] /* Simulate Events in Near Real-time */ \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-G Output_Log_Filename] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-F HEC_Output_Filename] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-f LEC_Output_Filename] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-s Fixed_RNG_Seed] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-t Fixed_Initial_Sim_Time(>=0)] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-O HEC_Init_Time_Offset(" TUNIT ")] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-o LEC_Init_Time_Offset(" TUNIT ")] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-D HEC_Photon_Propagation_Distance(m)] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-d LEC_Photon_Propagation_Distance(m)] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-L HEC_Photon_Loss_Fraction(>=0&&<=1)] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-l LEC_Photon_Loss_Fraction(>=0&&<=1)] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-m Detector_State_Error_Fraction(>=0&&<=1)] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-c Relative_Clock_Frequency_Diff(-)] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-n Number_Source_Emissions_to_Simulate(>0)] \\\n");
  I(log_fh, "%*s", (int)strlen(argv[0]) + 4, "");
  I(log_fh, "[-e Photon_Source_Emission_Rate(events/s)(>0)]\n");
  I(log_fh, "\n");
  I(log_fh, "This program is intended to generate correlated photon\n");
  I(log_fh, "events that mimic the output emanating from S-15 timestamp\n");
  I(log_fh, "cards. Events are generated for a High Event Count (HEC)\n");
  I(log_fh, "party -- typically Alice who is in possession of the photon\n");
  I(log_fh, "source -- and a Low Event Count (LEC) party -- typically Bob\n");
  I(log_fh, "who is physically removed from the photon source by some\n");
  I(log_fh, "propagation distance.\n");
  I(log_fh, "\n");
  I(log_fh, "Initial timing information is taken from Unix Epoch time in\n");
  I(log_fh, "nanoseconds from 00:00:00 UTC on 1 January 1970 or set by \n");
  I(log_fh, "the user. A fixed number of pair events may be generated or\n");
  I(log_fh, "the program may run indefinitely until a SIGINT or SIGTERM\n");
  I(log_fh, "is caught and handled. Timing between events can follow a \n");
  I(log_fh, "Poissonian Quantile Function with a 1/mean value given by\n");
  I(log_fh, "the -e option, or it can be set to uniform with the same\n");
  I(log_fh, "1/mean value. The code can run as fast as possible or in\n");
  I(log_fh, "near real-time, e.g. to accomodate a GUI.\n");
  I(log_fh, "\n");
  I(log_fh, "All HEC and LEC events will be written out to separate files.\n");
  I(log_fh, "Each party may experience some uniform loss fraction where\n");
  I(log_fh, "some percentage of photons do not propagate to the detectors\n");
  I(log_fh, "and thus not writing an event to the simulated timestamp\n");
  I(log_fh, "card.\n");
  I(log_fh, "\n");
  I(log_fh, "Each party may start off with an initial time offset value\n");
  I(log_fh, "(e.g. from NTP sync differences) and also can experience a\n");
  I(log_fh, "linear relative clock frequency drift. Each party may have\n");
  I(log_fh, "an associated propagation distance that translates into\n");
  I(log_fh, "a propagation time delay in timestamps.\n");
  I(log_fh, "\n");
  I(log_fh, "Detector event states will match when both HEC and LEC\n");
  I(log_fh, "parties choose the same measurment basis and with the\n");
  I(log_fh, "probability of 1 - (detector state error fraction)*100. With\n");
  I(log_fh, "probability of (detector state error fraction)*100 states\n");
  I(log_fh, "will be uncorrelated even if the same basis choice is made.\n");
  I(log_fh, "This is a mechanism to introduce controllable error (QBER).\n");
  I(log_fh, "\n");
  I(log_fh, "Please see code comments for how timing information is\n");
  I(log_fh, "transformed in a timestamp rawevent struct.\n");
  I(log_fh, "\n");
}

/* -------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------- */
/* -------------------------------------------------------------------------- */

int main(int argc, char *argv[]) {

  /* Initializations; No need to change */
/* -------------------------------------------------------------------------- */
  /* Used for option parsing */
  int opt = (int)0;
  /* Used for error handling */
  int error_code = (int)0;
  /* Used for option parsing error handling */
  bool parse_fail = false;
  /* Index of current photon creation event */
  Epoch event_index = ZERO;
  /* By default logging details go to stdout */
  FILE *log_fh = stdout;
  /* High event count file pointer */
  FILE *hec_fptr = NULL;
  /* Low event count file pointer */
  FILE *lec_fptr = NULL;
  /* High event counter rawevent output buffer */
  struct rawevent hec_outbuf = {(RE)0, (RE)0};
  /* Low event coutner rawevent output buffer */
  struct rawevent lec_outbuf = {(RE)0, (RE)0};
  /* Simulation initial time [TUNIT] */
  Epoch sim_init_time = ZERO;
  /* Simulation current time */
  Epoch sim_time = ZERO;
  /* Simulation time delta: start to finish */
  Epoch sim_time_delta = ZERO;
  /* Real initial time [TUNIT] */
  Epoch real_init_time = ZERO;
  /* Real time delta: start to finish */
  Epoch real_time_delta = ZERO;
  /* High event count initial timestamp sig */
  Epoch hec_anchor_signature = ZERO;
  /* Low event count initial timestamp sig */
  Epoch lec_anchor_signature = ZERO;
  /* High event count timestamp sig between events */
  Epoch hec_signature_between_events = ZERO * TSUNIT;
  /* Low event count timestamp sig between events */
  Epoch lec_signature_between_events = ZERO * TSUNIT;
  /* Pair of HEC and LEC party detector states */
  struct detstatepair ds_pair = {ZERO, ZERO};
  /* High event count detector state */
  Epoch hec_detector_state = ZERO;
  /* Low event count detector state */
  Epoch lec_detector_state = ZERO;
  /* Time between photon events */
  Epoch time_between_events = ZERO;
  /* Speed of light in a vacuum [m/s] */
  const Epoch speed_of_light = (Epoch)299792458;
  /* High event count propagate photon; reset below */
  bool hec_propagate_photon = (bool)true;
  /* Low event count propagate photon; reset below */
  bool lec_propagate_photon = (bool)true;
  /* High event count number of propagated events */
  Epoch hec_event_count = ZERO;
  /* Low event count number of propagated events */
  Epoch lec_event_count = ZERO;
  /* Count of detected quantum correlated events */
  Epoch det_state_true_match_count = ZERO;
  /* Initialization Seeds for PCG-based random number generation */
  Epoch entropy_seeds[2] = {ZERO};
  /* Variables used in real-time feedback control */
  Epoch sim_time_new = ZERO;
  Epoch sim_time_old = ZERO;
  Epoch real_time_new = ZERO;
  Epoch real_time_old = ZERO;
  Epoch event_index_old = ZERO;
  /* Keep tv_nsec > 0 to allow
   * multiplication alg to function properly */
  struct timespec sleep_interval;
  sleep_interval.tv_sec = (time_t)0;
  sleep_interval.tv_nsec = (long)1;
  /* Keep some minimum stride > 0 to allow
   * for non-trivial time diff to occur. */
  Epoch sleep_stride = (Epoch)100;
  /* Toggle to turn on real-time feedback loop */
  bool real_time = (bool)false;

  /* Default configuration options. Change these, if you wish */
/* -------------------------------------------------------------------------- */
  /* Toggle to run until signal or fixed event count */
  bool run_indefinitely = (bool)false;
  /* Toggle to make initial sim time and random seed fixed */
  bool reproducible_time = (bool)false;
  /* Toggle to make each event occur with uniform time int */
  bool uniform_events = (bool)false;
  /* File for high event count photon events to be written */
  /* NOTE: "stdout" has reserved meaning in the code. */
  char *log_filename = (char *)"stdout";
  /* File for high event count photon events to be written */
  char *hec_filename = (char *)"events.hec.out";
  /* File for low event count photon events to be written */
  char *lec_filename = (char *)"events.lec.out";
  /* RNG fixed seed if reproducible_time == true */
  Epoch fixed_seed = (Epoch)123456789;
  /* Fixed initial simulation time [TUNIT since epoch] if rt=t */
  Epoch fixed_init_time = (Epoch)1587318692304817123;
  /* High event count initial clock offset (NTP variation) [TUNIT] */
  Epoch hec_time_offset = ZERO;
  /* Low event count initial clock offset (NTP variation) [TUNIT] */
  Epoch lec_time_offset = ZERO;
  /* HEC photon propagation distance [m] */
  Epoch hec_propagation_distance = (Epoch)0;
  /* LEC photon propagation distance [m] */
  Epoch lec_propagation_distance = (Epoch)0;
  /* High event count fraction of photons lost before write */
  double hec_loss_fraction = (double)0;
  /* Low event count fraction of photons lost before write */
  double lec_loss_fraction = (double)0;
  /* Fraction of same basis uncorrelated detector states for HEC/LEC [0,1] */
  double det_state_error_fraction = (double)0;
  /* Clock frequency difference between HEC and LEC sides */
  /* NOTE: From DSTA3 Report: 6E-12 for two Rb clocks */
  double clock_freq_diff = (double)0;
  /* Number of source photon events if run_indefinitely==f */
  Epoch source_num_emissions = (Epoch)2E6;
  /* How often a photon emission occurs [events/s] */
  double source_emission_rate = (double)1E5;
  /* Detector state mapping from HEC party to LEC party */
  /*     1 2 4 8 (detector click 0001 0010 0100 1000)
   * HEC V - H +
   * LEC H + V -
   * qcrypto default => 4 8 1 2
   */
  Epoch det_map_correlated[] = {(Epoch)4, (Epoch)8, (Epoch)1, (Epoch)2};
  Epoch det_map_uncorrelated[] = {(Epoch)1, (Epoch)2, (Epoch)4, (Epoch)8};


/* -------------------------------------------------------------------------- */

  /* Register function for handling captured signals */
  signal(SIGINT, signal_handler);  /* control+c */
  signal(SIGTERM, signal_handler); /* kill -15 */

  /* Parsing command-line arguments */
  opterr = 1;
  while ((opt = getopt(argc, argv, "vqiruRG:F:f:s:t:O:o:D:d:L:l:m:c:n:e:h")) !=
         EOF) {
    switch (opt) {
    case 'v': /* increase verbosity */
      D(log_fh, "SET: -v verbosity:                %d\n", verbosity);
      verbosity += 1;
      break;
    case 'q': /* decrease verbosity */
      D(log_fh, "SET: -q verbosity:                %d\n", verbosity);
      verbosity -= 1;
      break;
    case 'i': /* run indefinitely */
      run_indefinitely = true;
      D(log_fh, "SET: -i run_indefinitely:         %s\n",
        run_indefinitely ? "true" : "false");
      break;
    case 'r': /* reproducible time & random numbers */
      reproducible_time = true;
      D(log_fh, "SET: -r reproducible_time:        %s\n",
        reproducible_time ? "true" : "false");
      break;
    case 'u': /* uniform time between events */
      uniform_events = true;
      D(log_fh, "SET: -u uniform_events:           %s\n",
        uniform_events ? "true" : "false");
      break;
    case 'R': /* feedback loop to run code in real-time */
      real_time = true;
      D(log_fh, "SET: -R real_time:                %s\n",
        real_time ? "true" : "false");
      break;
    case 'G': /* log filename */
      log_filename = optarg;
      D(log_fh, "SET: -G log_filename:             %s\n", log_filename);
      break;
    case 'F': /* HEC filename */
      hec_filename = optarg;
      D(log_fh, "SET: -F hec_filename:             %s\n", hec_filename);
      break;
    case 'f': /* LEC filename */
      lec_filename = optarg;
      D(log_fh, "SET: -f lec_filename:             %s\n", lec_filename);
      break;
    case 's': /* fixed seed for RNG */ /* TODO: Could, in theory be negative */
      fixed_seed = (Epoch)strtoull(optarg, NULL, 10);
      D(log_fh, "SET: -s fixed_seed:               %" EF "\n", fixed_seed);
      break;
    case 't': /* fixed initialization time */ /* TODO: Could input negative
                                                 currently */
      fixed_init_time = (Epoch)strtoull(optarg, NULL, 10);
      D(log_fh, "SET: -t fixed_init_time:          %" EF "\n", fixed_init_time);
      break;
    case 'O': /* HEC time offset */ /* TODO: Could, in theory be negative */
              /* NOTE: use strtod to be able to use scientific notation
               * on the command line. Mostly convienence. */
      hec_time_offset = (Epoch)strtod(optarg, NULL);
      D(log_fh, "SET: -O hec_time_offset:          %" EF "\n", hec_time_offset);
      break;
    case 'o': /* LEC time offset */ /* TODO: Could, in theory be negative */
              /* NOTE: use strtod to be able to use scientific notation
               * on the command line. Mostly convienence. */
      lec_time_offset = (Epoch)strtod(optarg, NULL);
      D(log_fh, "SET: -o lec_time_offset:          %" EF "\n", lec_time_offset);
      break;
    case 'D': /* HEC propagation distance */
      hec_propagation_distance = (Epoch)strtoull(optarg, NULL, 10);
      D(log_fh, "SET: -D hec_propagation_distance: %" EF "\n",
        hec_propagation_distance);
      break;
    case 'd': /* LEC propagation distance */
      lec_propagation_distance = (Epoch)strtoull(optarg, NULL, 10);
      D(log_fh, "SET: -d lec_propagation_distance: %" EF "\n",
        lec_propagation_distance);
      break;
    case 'L': /* HEC loss fraction */
      hec_loss_fraction = (double)strtod(optarg, NULL);
      D(log_fh, "SET: -L hec_loss_fraction:        %f\n", hec_loss_fraction);
      if (hec_loss_fraction < (double)0 || hec_loss_fraction > (double)1) {
        C(log_fh, "FAIL: 0 <= hec_loss_fraction <= 1; Line: %d\n", __LINE__);
        parse_fail = true;
      }
      break;
    case 'l': /* LEC loss fraction */
      lec_loss_fraction = (double)strtod(optarg, NULL);
      D(log_fh, "SET: -l lec_loss_fraction:        %f\n", lec_loss_fraction);
      if (lec_loss_fraction < (double)0 || lec_loss_fraction > (double)1) {
        C(log_fh, "FAIL: 0 <= lec_loss_fraction <= 1; Line: %d\n", __LINE__);
        parse_fail = true;
      }
      break;
    case 'm': /* detector state error fraction */
      det_state_error_fraction = (double)strtod(optarg, NULL);
      D(log_fh, "SET: -m det_state_error_fraction: %f\n",
        det_state_error_fraction);
      if (det_state_error_fraction < (double)0 ||
          det_state_error_fraction > (double)1) {
        C(log_fh, "FAIL: 0 <= det_state_error_fraction <= 1; Line: %d\n",
          __LINE__);
        parse_fail = true;
      }
      break;
    case 'c': /* relative clock frequency difference */
      clock_freq_diff = (double)strtod(optarg, NULL);
      D(log_fh, "SET: -c clock_freq_diff:          %E\n", clock_freq_diff);
      break;
    case 'n': /* source number of photon emissions to simulate */
              /* NOTE: use strtod to be able to use scientific notation
               * on the command line. Mostly convienence. */
      source_num_emissions = (Epoch)strtod(optarg, NULL);
      D(log_fh, "SET: -n source_num_emissions:     %" EF "\n",
        source_num_emissions);
      if (strtod(optarg, NULL) <= (Epoch)0) {
        C(log_fh, "FAIL: 0 < source_num_emissions; Line: %d\n", __LINE__);
        parse_fail = true;
      }
      break;
    case 'e': /* source photon emission rate [s] */
      source_emission_rate = (double)strtod(optarg, NULL);
      D(log_fh, "SET: -e source_emission_rate:     %E\n", source_emission_rate);
      if (source_emission_rate <= (double)0) {
        C(log_fh, "FAIL: 0 < source_emission_rate; Line: %d\n", __LINE__);
        parse_fail = true;
      }
      break;
    case 'h': /* ask for help */
      D(log_fh, "SET: -h program help\n");
      display_usage(log_fh, argv);
      /* No error but shortcut to show usage only */
      error_code = (int)0;
      goto error;
      break;
    case '?': /* unknown options */
      parse_fail = true;
      break;
    default: /* should not get here */
      parse_fail = true;
      C(log_fh, "Option parse unknown error; Line: %d\n", __LINE__);
      break;
    }
  }

  /* Handle when there was a parsing failure and quit */
  if (parse_fail) {
    display_usage(log_fh, argv);
    C(log_fh, "Parse Option Error; Line: %d\n", __LINE__);
    error_code = (int)1;
    goto error;
  }

/* -------------------------------------------------------------------------- */
/* Input-dependent initialization */

  if (strncmp(log_filename, "stdout", 6) != 0) {
    log_fh = fopen(log_filename, "w");
  }

  /* Start the real time clock */
  if ((real_init_time = nanoseconds_since_epoch(log_fh) / (Epoch)T2NS) ==
      ZERO) {
    C(log_fh, "Timer Initialization Error; Line: %d\n", __LINE__);
    error_code = (int)2;
    goto error;
  }

  /* Get the same results between runs */
  if (reproducible_time) {
    /* Fix the seed value for RNG */
    entropy_seeds[0] = fixed_seed;
    entropy_seeds[1] = fixed_seed;
    /* Fix the initial sim time input */
    sim_init_time = fixed_init_time;
  } else {
    /* Use current nanoseconds since epoch as initial simulation time */
    sim_init_time = real_init_time;
    /* Seed initial values from a kernel source */
    get_entropy((void*)entropy_seeds, sizeof(entropy_seeds));
  }

  /* Initialize simulation time */
  sim_time = sim_init_time;

  /* Initialize real-time feedback variables */
  sim_time_new = sim_init_time;
  sim_time_old = sim_init_time;
  real_time_new = real_init_time;
  real_time_old = real_init_time;

  /* Initialize RNG */
  pcg32_srandom((uint64_t)entropy_seeds[0], (uint64_t)entropy_seeds[1]);

/* -------------------------------------------------------------------------- */

  /* Convert initial time into timestamp signature with initial offsets */
  hec_anchor_signature =
      (sim_init_time + clock_skew(hec_time_offset, clock_freq_diff, ZERO)) *
      TSUNIT;
  lec_anchor_signature =
      (sim_init_time + clock_skew(lec_time_offset, clock_freq_diff, ZERO)) *
      TSUNIT;

  /* Initialize signatures to our anchors */
  hec_signature_between_events = hec_anchor_signature;
  lec_signature_between_events = lec_anchor_signature;

  /* Configuration check */
  I(log_fh, "Maximum Epoch Number:                         %" EF "\n",
    (Epoch)~0);
  I(log_fh, "Real Epoch Time " TUNIT ":                         %" EF "\n",
    real_init_time);
  I(log_fh, "Run program Indefinitely:                     %s\n",
    run_indefinitely ? "true" : "false");
  I(log_fh, "Run with reproducible time & random numbers:  %s\n",
    reproducible_time ? "true" : "false");
  I(log_fh, "Run with uniform time between events:         %s\n",
    uniform_events ? "true" : "false");
  I(log_fh, "Simulation Attempting to Run in Real-time:    %s\n",
    real_time ? "true" : "false");
  I(log_fh, "Log filename:                                 %s\n", log_filename);
  I(log_fh, "HEC output filename:                          %s\n", hec_filename);
  I(log_fh, "LEC output filename:                          %s\n", lec_filename);
  if (reproducible_time) {
    I(log_fh, "Fixed RNG Seed                                %" EF " %" EF "\n",
      entropy_seeds[0], entropy_seeds[1]);
    I(log_fh, "Fixed Initial Simulation Time:                %" EF "\n",
      sim_init_time);
  } else {
    I(log_fh, "Initial Simulation Time:                      %" EF "\n",
      sim_init_time);
    I(log_fh, "RNG Seed:                                     %" EF " %" EF "\n",
      entropy_seeds[0], entropy_seeds[1]);
  }
  I(log_fh, "High Event Count (HEC) Anchor Signature:      %" EF "\n",
    hec_anchor_signature);
  I(log_fh, "Low Event Count (LEC) Anchor Signature:       %" EF "\n",
    lec_anchor_signature);
  I(log_fh, "High Event Count (HEC) Anchor Signature(hex): %x\n",
    hec_anchor_signature);
  I(log_fh, "Low Event Count (LEC) Anchor Signature(hex):  %x\n",
    lec_anchor_signature);
  I(log_fh, "HEC Initial Clock Offset " TUNIT ":                %E\n",
    (double)hec_time_offset);
  I(log_fh, "LEC Initial Clock Offset " TUNIT ":                %E\n",
    (double)lec_time_offset);
  I(log_fh, "HEC Photon Propagation Distance [m]:          %" EF "\n",
    hec_propagation_distance);
  I(log_fh, "LEC Photon Propagation Distance [m]:          %" EF "\n",
    lec_propagation_distance);
  I(log_fh, "HEC Photon Loss Fraction [-]:                 %.2f\n",
    hec_loss_fraction);
  I(log_fh, "LEC Photon Loss Fraction [-]:                 %.2f\n",
    lec_loss_fraction);
  I(log_fh, "Detector State Error Fraction [-]:            %.2f\n",
    det_state_error_fraction);
  I(log_fh, "Clock Relative Frequency Difference [-]:      %E\n",
    clock_freq_diff);
  if (!run_indefinitely) {
    I(log_fh, "Number Of Source Emission Events:             %E\n",
      (double)source_num_emissions);
  }
  if (uniform_events) {
    I(log_fh, "Uniform Source Emission Rate [events/s]:      %E\n",
      source_emission_rate);
  } else {
    I(log_fh, "Poissonian Source Emission Rate [events/s]:   %E\n",
      source_emission_rate);
  }
  I(log_fh,
    "Detector Mapping between HEC and LEC Parties: %" EF "%" EF "%" EF "%" EF
    "\n",
    det_map_correlated[0], det_map_correlated[1], det_map_correlated[2],
    det_map_correlated[3]);
  I(log_fh,
    "Matching Basis Uncorrelated Detector Mapping: %" EF "%" EF "%" EF "%" EF
    "\n",
    det_map_uncorrelated[0], det_map_uncorrelated[1], det_map_uncorrelated[2],
    det_map_uncorrelated[3]);

  /* --------------------------------------------------------------------------
   */
  /* Startup the event generation loop */

  /* The hec and lec files for writing */
  hec_fptr = fopen(hec_filename, "wb");
  if (hec_fptr == NULL) {
    C(log_fh, "Failed to open hec_fptr; Line: %d\n", __LINE__);
    goto error;
  }
  lec_fptr = fopen(lec_filename, "wb");
  if (lec_fptr == NULL) {
    C(log_fh, "Failed to open lec_fptr; Line: %d\n", __LINE__);
    goto error;
  }

  I(log_fh, "\n");
  I(log_fh, "Beginning Simulation Loop...\n");

  event_index_old = ZERO;
  event_index = ZERO;
  /* Fixed number of events or indefinite and not interrupted */
  while ((event_index < source_num_emissions || (run_indefinitely)) &&
         !interrupted) {

    /* Mechanism for slowing the output to near real time speeds */
    if ((event_index - event_index_old) > sleep_stride && real_time) {
      /* Use mean time between events to smooth feedback loop */
      sim_time_new += (Epoch)((double)TCONV / source_emission_rate);
      sim_time_delta = sim_time_new - sim_time_old;
      sim_time_old = sim_time_new;
      real_time_old = real_time_new;
      real_time_new = nanoseconds_since_epoch(log_fh) / (Epoch)T2NS;
      real_time_delta = real_time_new - real_time_old;
      event_index_old = event_index;
      /* Keep nanosleep for a near-constant overhead function call */
      clock_nanosleep(CLOCK_MONOTONIC, (int)0, &sleep_interval, NULL);
      /* At least 1 but larger if real_time > sim_time */
      sleep_stride =
          MAX((Epoch)1, (double)real_time_delta / (sim_time_delta + (Epoch)1));
      /* Further control overhead by manipulating sleep time */
      /* sleep_stride == 1 means this being called every iteration
       * and is still not generating enough over head. Therefore,
       * slow it down by increasing sleep time. */
      if (sleep_stride == 1) {
        sleep_interval.tv_nsec *= 10;
      }
      /* sleep_stride is now away from 1 and there is a non-trivial
       * sleep_interval. Lower interval so that feedback can have a 
       * mechanism to reduce overhead to stay near real-time. */
      else if (sleep_stride > 1 && sleep_interval.tv_nsec >= 10) {
        sleep_interval.tv_nsec /= 10;
      }
#if DEBUG
      I(log_fh, "EI: %" EF " RTD: %" EF " STD: %" EF " SS: %" EF " SI: %ld\n",
             event_index, real_time_delta, sim_time_delta, sleep_stride,
             sleep_interval.tv_nsec);
#endif
    }

    /* Generate correlated detector states */
    ds_pair = generate_detector_state_pair(
        det_map_correlated, det_map_uncorrelated, det_state_error_fraction);
    hec_detector_state = ds_pair.hec_state;
    lec_detector_state = ds_pair.lec_state;
    /* The match will be a 0 (false) or 1 (true) */
    det_state_true_match_count += (Epoch)ds_pair.match;

    if (uniform_events) {
      /* Generate how long until next event - uniform distribution */
      /* Assumes source_emission_rate is given in [events/s] 
       * converting to [events/TUNIT] */
      time_between_events = (Epoch)((double)TCONV / source_emission_rate);
    } else {
      /* Generate how long until next event - poissonian distribution */
      /* Assumes source_emission_rate is given in [events/s] 
       * converting to [events/TUNIT] */
      time_between_events =
          (Epoch)quantile_exp((double)1 / (double)TCONV * source_emission_rate);
    }

    /* Keep track of simulated time */
    sim_time += time_between_events;

    /* Debug log time between events */
#if DEBUG
    D(log_fh,
      "%" EF "; time between events " TUNIT ": %" EF
      "; Cumulative Sim Time " TUNIT ": %" EF "\n",
      event_index, time_between_events, sim_time);
#endif

    /* Propagate from source to HEC detectors; convert to timestamp signature */
    /* NOTE: Order and cast chosen to try and preserve significant digits */
    /* Assumes: prop distance [m]; speed of light [m/s]; time [TUNIT] */
    hec_signature_between_events +=
        time_between_events * TSUNIT +
        (Epoch)((double)(hec_propagation_distance * (Epoch)TCONV * TSUNIT) /
                (double)speed_of_light);
    /* Propagate from source to LEC detectors */
    /* And add in linear clock skew - formula only needs time delta */
    /* NOTE: Initial offset is already accounted for and should be 0 here */
    /* Convert to timestamp signature */
    lec_signature_between_events +=
        time_between_events * TSUNIT +
        (Epoch)((double)(lec_propagation_distance * (Epoch)TCONV * TSUNIT) /
                (double)speed_of_light) +
        clock_skew(ZERO, clock_freq_diff, time_between_events) * TSUNIT;

    /* Split out timestamp signatures accordinly to make choppers happy */
    /*
     * Given raw event bit information (example raw bit string):
     * SpeQtralQuantumTechnologiesSpecializeInQuantumKeyDistributionFun
     *
     * Upper 32-bit RE (outbuf.cv):
     *
     * (Reading right to left => least significant bits up to 64 bits)
     *    6         5         4         3         2         1
     * 3210987654321098765432109876543210987654321098765432109876543210
     * (Reading left to right => most significant bits up to 64 bits)
     *           1         2         3         4         5         6
     * 0123456789012345678901234567890123456789012345678901234567890123
     * SpeQtralQuantumTechnologiesSpecializeInQuantumKeyDistributionFun
     *
     * >> 17: Bit shift 17 to the right
     *
     *           1         2         3         4         5         6
     * 0123456789012345678901234567890123456789012345678901234567890123
     * 00000000000000000SpeQtralQuantumTechnologiesSpecializeInQuantumK
     *
     * & 0xffffffff: Mask to get lower 32 bits only
     *
     *           1         2         3         4         5         6
     * 0123456789012345678901234567890123456789012345678901234567890123
     * 0000000000000000000000000000000011111111111111111111111111111111
     * 00000000000000000000000000000000TechnologiesSpecializeInQuantumK
     *
     * (RE): cast to 32-bit number
     *
     *           1         2         3         4         5         6
     * 0123456789012345678901234567890123456789012345678901234567890123
     *                     outbuf.cv = TechnologiesSpecializeInQuantumK
     *
     * Lower 32-bit RE (outbuf.dv):
     *
     * (Reading right to left => least significant bits)
     *    6         5         4         3         2         1
     * 3210987654321098765432109876543210987654321098765432109876543210
     * (Reading left to right => most significant bits)
     *           1         2         3         4         5         6
     * 0123456789012345678901234567890123456789012345678901234567890123
     * SpeQtralQuantumTechnologiesSpecializeInQuantumKeyDistributionFun
     *
     * & 0x0001ffff: Mask to get lower 17 bits only
     *
     *    6         5         4         3         2         1
     * 3210987654321098765432109876543210987654321098765432109876543210
     * 0000000000000000000000000000000000000000000000011111111111111111
     * 00000000000000000000000000000000000000000000000eyDistributionFun
     *
     * << 15: Bit shift 15 to the right
     *
     *    6         5         4         3         2         1
     * 3210987654321098765432109876543210987654321098765432109876543210
     * 00000000000000000000000000000000eyDistributionFun000000000000000
     *
     * + detector_state: Add in 4-bit detector state
     *
     *    6         5         4         3         2         1
     * 3210987654321098765432109876543210987654321098765432109876543210
     * 00000000000000000000000000000000eyDistributionFun000000000000000
     *+0000000000000000000000000000000000000000000000000000000000001111
     * 00000000000000000000000000000000eyDistributionFun000000000001111
     *
     * (RE): cast to 32-bit number
     *
     *    6         5         4         3         2         1
     * 3210987654321098765432109876543210987654321098765432109876543210
     *                     outbuf.dv = eyDistributionFun000000000001111
     *
     * struct rawevent { cv; dv;} outbuf; :
     *           1         2         3         4         5         6
     * 0123456789012345678901234567890123456789012345678901234567890123
     * TechnologiesSpecializeInQuantumKeyDistributionFun000000000001111
     *
     * Detection time in the most significant 49 bits in multiples of
     * 125 ps with detector state information in the least significant
     * 4 bits.
     */

    /* Bit shift 17 to the right; take lower 32 bits */
    hec_outbuf.cv =
        (RE)((hec_signature_between_events >> (Epoch)17) & (Epoch)0xffffffff);
    lec_outbuf.cv =
        (RE)((lec_signature_between_events >> (Epoch)17) & (Epoch)0xffffffff);

    /* Take lower 17 bits; bit shift 15 to the left; add detector state in lower
     * 4 bits */
    hec_outbuf.dv =
        (RE)(((hec_signature_between_events & (Epoch)0x0001ffff) << (Epoch)15) +
             hec_detector_state);
    lec_outbuf.dv =
        (RE)(((lec_signature_between_events & (Epoch)0x0001ffff) << (Epoch)15) +
             lec_detector_state);

    /* Sanity checking */
#if DEBUG
    B(log_fh, "Detector State; HEC:             ", hec_detector_state, true);
    B(log_fh, "Detector State; LEC:             ", lec_detector_state, false);
    B(log_fh, "HEC Signature in between events: ", hec_signature_between_events,
      true);
    B(log_fh, "LEC Signature in between events: ", lec_signature_between_events,
      false);
    B(log_fh, "HEC outbuf.cv:                   ", hec_outbuf.cv, true);
    B(log_fh, "LEC outbuf.cv:                   ", lec_outbuf.cv, false);
    B(log_fh, "HEC outbuf.dv:                   ", hec_outbuf.dv, true);
    B(log_fh, "LEC outbuf.dv:                   ", lec_outbuf.dv, false);
#endif

    /* See if we propagate a photon to the detectors or lose it */
    hec_propagate_photon = check_photon_loss(hec_loss_fraction);
    lec_propagate_photon = check_photon_loss(lec_loss_fraction);

    /* Write out the rawevent buffer for high event count side (Alice) */
    if (hec_propagate_photon) {
      hec_event_count += (Epoch)1;
      fwrite(&hec_outbuf, sizeof(struct rawevent), (size_t)1, hec_fptr);
    }

    /* Write out the rawevent buffer for low event count side (Bob) */
    if (lec_propagate_photon) {
      lec_event_count += (Epoch)1;
      fwrite(&lec_outbuf, sizeof(struct rawevent), (size_t)1, lec_fptr);
    }

    /* Iterate onwards! */
    event_index += (Epoch)1;

    /* Create a litte spinner for stdout */
#if DEBUG
    if (event_index % (Epoch)500000 == ZERO && log_fh == stdout) {
      I(log_fh, "\r%s ", spinner[spindex++]);
      fflush(log_fh);
      if (spindex > (int)3) {
        spindex = (int)0;
      }
    }
#endif
  }

  /* Calculate how much simulation time passed */
  sim_time_delta = sim_time - sim_init_time;

  /* Stop the real time clock */
  if ((real_time_delta = nanoseconds_since_epoch(log_fh) / (Epoch)T2NS) ==
      ZERO) {
    C(log_fh, "Timer Initialization Error; Line: %d\n", __LINE__);
    error_code = (int)3;
    goto error;
  }
  /* Calculate how much real time passed */
  real_time_delta = real_time_delta - real_init_time;

  /* Summary */
  I(log_fh, "\n");
  I(log_fh, "Number of simulated events:                   %" EF "\n",
    event_index);
  I(log_fh, "Number of HEC events:                         %" EF "\n",
    hec_event_count);
  I(log_fh, "Number of LEC events:                         %" EF "\n",
    lec_event_count);
  I(log_fh, "Number of True Detector State Match Events:   %" EF "\n",
    det_state_true_match_count);
  I(log_fh, "True Match Ratio:                             %lf\n",
    (double)det_state_true_match_count / (double)event_index);
  I(log_fh, "Real Time Delta " TUNIT ":                         %" EF "\n",
    real_time_delta);
  I(log_fh, "Simulation Time Delta " TUNIT ":                   %" EF "\n",
    sim_time_delta);
  I(log_fh, "Time Ratio:                                   %lf\n",
    (double)sim_time_delta / (double)real_time_delta);
  I(log_fh, "# of Mutually Detected Pairs / Real Time [s]: %lE\n",
    (double)MIN(hec_event_count, lec_event_count) / (double)real_time_delta * TCONV);

  /* Standard cleanup */
  error:

  /* Close the file handles */
  if (hec_fptr != NULL) {
    fclose(hec_fptr);
  }
  if (lec_fptr != NULL) {
    fclose(lec_fptr);
  }
  if (log_fh != NULL) {
    fclose(log_fh);
  }

  /* Zero on clean exit */
  return error_code;

}
