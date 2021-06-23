# QKD Configuration

Find the [qkd_config](../common/qkd_config) file in the common configuration directory.

Interesting options include:
```bash
# esim config settings
export           num_events=5E4       # Total number of events to simulate
export source_emission_rate=1E3       # Event rate [events/second]
export      lec_time_offset=1E0       # LEC party time offset [nanoseconds]
export        lec_loss_frac=0.0       # LEC Loss Fraction [0(no loss)<=fraction<=1(all loss)]
export           error_frac=0.0       # Simulated QBER [0<=fraction<=1]
export  relative_freq_drift=0.0

# error correction config settings
export ec_min_bits=1024               # minimal number of raw bits to process in error correction
```

The idea is that a simulator called `esim` (event simulator - an event being an entangled photon pair creation event from 'magic crystals', i.e. SPDC) writes out binary files for the High Event Count (HEC) party and Low Event Count (LEC) party:
```bash
./esim                            \
-n ${num_events}                  \
-e ${source_emission_rate}        \
-c ${relative_freq_drift}         \
-o ${lec_time_offset}             \
-l ${lec_loss_frac}               \
-m ${error_frac}                  \
-F ${data_dir}/hec/events.hec.out \
-f ${data_dir}/lec/events.lec.out \
${verbosity}
```

Where all parameters are set inside the `run_esim` script in the `qkd/qsim` directory. 
* `num_events` is the number of events to simulate
* `source_emission_rate` control the events/s generated
* `relative_freq_drift` is the relative clock frequency drift between HEC and LEC party clocks
* `lec_time_offset` controls the time lag of the LEC party in ns
* `lec_loss_frac` controls what fraction of single photons from an entangled pair make it from the HEC party to the LEC party (Signal loss - sometimes calculated in negative decibels dB)
* `error_frac` is a stand-in for simulated QBER; 0 being no error; 1 being 100% error; somewhere around 0.11 (11% would be the max allowed under the protocol)
* The `-f` and `-F` options controls where the raw binary output files are directed
* `-v` for verbosity is standard output; `-vv` dumps more information; etc.

These events are fed into S-Fifteen's/Christian's `qcrypto` software stack to process, sift, and error correct until final keying material is agreed upon by the HEC and LEC parties.

## REST API Performance Considerations

NOTE: `ec_min_bits` controls how much final keying material is gathered before going through the CASCADE error correction and subsequent privacy amplification. This matters because it determines the number of bytes in any given final epoch file. Since a final epoch file is consumed into the local Vault instance as one 'key block'.

If `ec_min_bits` is set small (e.g. 256 bits - qcrypto default is 5000 bits) then you will end up with a lot of small files making lots of small key blocks in Vault. This, in theory, should allow for more simultaneous outstanding requests from SAEs as at least one key block is reserved for each request. Of course, this also increases communication overhead as more and more stuff is flying around in TLS communcation. If there were only a few key blocks to reserve, then outstanding requests may begin to pile up waiting to be able to reserve a key block for processing.

On the other hand. If the key blocks are too small, then multiple blocks will need to be reserved and consumed to meet one outstanding key request. It is up to the operator to heuristically try out different `ec_min_bits` sizes depending on the size of the incomding SAE key requests and the typical number of outstanding concurrent requests.

I sense a fun project for someone who is interested in seeing the limits in this fairly high dimensional space. You also have to consider the hardware backing the Vault and REST services too. Certainly a Raspberry Pi isn't going to keep up with a nice high-end server-class high-GHz chip from Intel or AMD.

## esim Options

The simulator supports lots of stuff. The majority is not terribly relevant but I think it is fun:
```bash
$ ./esim -h
[INFO]
[INFO] Usage for ./esim:
[INFO]
[INFO]     ./esim \
[INFO]           [INFO] [-h] /* Display This Help Message And Quit */ \
[INFO]           [INFO] [-v] /* Increase Verbosity By One */ \
[INFO]           [INFO] [-q] /* Decrease Verbosity By One */ \
[INFO]           [INFO] [-i] /* Run Indefinitely Until Signal */ \
[INFO]           [INFO] [-r] /* Reproducible Initial Time & RNG Sequence */ \
[INFO]           [INFO] [-u] /* Simulate Uniform Time Between Photon Events */ \
[INFO]           [INFO] [-R] /* Simulate Events in Near Real-time */ \
[INFO]           [INFO] [-G Output_Log_Filename] \
[INFO]           [INFO] [-F HEC_Output_Filename] \
[INFO]           [INFO] [-f LEC_Output_Filename] \
[INFO]           [INFO] [-s Fixed_RNG_Seed] \
[INFO]           [INFO] [-t Fixed_Initial_Sim_Time(>=0)] \
[INFO]           [INFO] [-O HEC_Init_Time_Offset([ns])] \
[INFO]           [INFO] [-o LEC_Init_Time_Offset([ns])] \
[INFO]           [INFO] [-D HEC_Photon_Propagation_Distance(m)] \
[INFO]           [INFO] [-d LEC_Photon_Propagation_Distance(m)] \
[INFO]           [INFO] [-L HEC_Photon_Loss_Fraction(>=0&&<=1)] \
[INFO]           [INFO] [-l LEC_Photon_Loss_Fraction(>=0&&<=1)] \
[INFO]           [INFO] [-m Detector_State_Error_Fraction(>=0&&<=1)] \
[INFO]           [INFO] [-c Relative_Clock_Frequency_Diff(-)] \
[INFO]           [INFO] [-n Number_Source_Emissions_to_Simulate(>0)] \
[INFO]           [INFO] [-e Photon_Source_Emission_Rate(events/s)(>0)]
[INFO]
[INFO] This program is intended to generate correlated photon
[INFO] events that mimic the output emanating from S-15 timestamp
[INFO] cards. Events are generated for a High Event Count (HEC)
[INFO] party -- typically Alice who is in possession of the photon
[INFO] source -- and a Low Event Count (LEC) party -- typically Bob
[INFO] who is physically removed from the photon source by some
[INFO] propagation distance.
[INFO]
[INFO] Initial timing information is taken from Unix Epoch time in
[INFO] nanoseconds from 00:00:00 UTC on 1 January 1970 or set by
[INFO] the user. A fixed number of pair events may be generated or
[INFO] the program may run indefinitely until a SIGINT or SIGTERM
[INFO] is caught and handled. Timing between events can follow a
[INFO] Poissonian Quantile Function with a 1/mean value given by
[INFO] the -e option, or it can be set to uniform with the same
[INFO] 1/mean value. The code can run as fast as possible or in
[INFO] near real-time, e.g. to accomodate a GUI.
[INFO]
[INFO] All HEC and LEC events will be written out to separate files.
[INFO] Each party may experience some uniform loss fraction where
[INFO] some percentage of photons do not propagate to the detectors
[INFO] and thus not writing an event to the simulated timestamp
[INFO] card.
[INFO]
[INFO] Each party may start off with an initial time offset value
[INFO] (e.g. from NTP sync differences) and also can experience a
[INFO] linear relative clock frequency drift. Each party may have
[INFO] an associated propagation distance that translates into
[INFO] a propagation time delay in timestamps.
[INFO]
[INFO] Detector event states will match when both HEC and LEC
[INFO] parties choose the same measurment basis and with the
[INFO] probability of 1 - (detector state error fraction)*100. With
[INFO] probability of (detector state error fraction)*100 states
[INFO] will be uncorrelated even if the same basis choice is made.
[INFO] This is a mechanism to introduce controllable error (QBER).
[INFO]
[INFO] Please see code comments for how timing information is
[INFO] transformed in a timestamp rawevent struct.
[INFO]
```

# Inspecting the QKD Docker Image

Creating an emphemeral docker container for inspection only; i.e. this doesn't create persistent keys to use with Guardian:

```bash
$ docker image ls | grep guardian
guardian_rest                 latest           764882fb3545   11 days ago     111MB
guardian_unsealer             latest           457b6ae2a9dc   12 days ago     335MB
guardian_qkd                  latest           2dde8bde34ac   12 days ago     303MB
guardian_watcher              latest           bbb0dd90f193   12 days ago     306MB
guardian_notifier             latest           c3cd2780b9be   12 days ago     67.6MB
guardian_vault_init_phase_2   latest           48e5003a7415   12 days ago     52.7MB
guardian_vault_init           latest           48e5003a7415   12 days ago     52.7MB
guardian_certauth             latest           49ff6ca4e323   12 days ago     6.51MB
guardian_certauth_csr         latest           49ff6ca4e323   12 days ago     6.51MB

# Mimicking the docker-compose bind mount for the QKD configuration file
# Also modifying the entrypoint to '/bin/bash' from 'make'
# Note the location the command is run from and note the $(pwd) as absolute paths are required to properly mount the qkd_config file
$ cd ${TOP_DIR}
$ docker run -it --rm --mount type=bind,source=$(pwd)/common/qkd_config,target=/root/code/qsim/qkd_config --entrypoint /bin/bash guardian_qkd
```

We start a container (interactively '-i' with a psuedo-TTY '-t') from the guardian_qkd image that lauches /bin/bash and mounts in the qkd_config file. It destroys itself (--rm) upon exit.

Inside the container:
```bash
bash-5.1# pwd
/root/code/qsim
bash-5.1# ls
Makefile  epoch_files  qkd_config  run_chopper	run_chopper2  run_copy	run_costream  run_diagbb84  run_ec  run_esim  run_getrate  run_pfind  run_splicer  src
```

Makefile targets:
```bash
SHELL := /bin/bash
setup: link

link: esim
	ln -sf ./src/esim

esim:
	+$(MAKE) -C ./src

ctest: clean link
	./run_esim
	./run_chopper lec
	./run_chopper2 hec
	./run_getrate hec
	./run_getrate lec
	./run_pfind
	./run_costream
	./run_splicer
	./run_ec
	./run_copy hec
	./run_copy lec

.PHONY: clean allclean distclean
clean:
	rm -rf hec
	rm -rf lec
	rm -f *.pipe
	rm -f *.log
	rm -f *_tlog
	rm -f *.out
	rm -f *.bin
	find -type d \( -name "*.hec" -o -name "*.lec" \) -exec rm -rf {} +
	+$(MAKE) -C ./src clean

allclean: clean
	rm -f esim
	# Only delete copied epoch files here; otherwise, can lead to removal
	# and desync between local and remote KMEs because epoch files were
	# destroyed before consumed by the other side.
	rm -rf ./epoch_files/*
	+$(MAKE) -C ./src allclean

distclean: allclean
	+$(MAKE) -C ./src distclean
```

To mimick what happens during a 'make keys' target call in guardian:
```bash
$ make ctest
```

This clears any residual files out, compiles the `esim` entangled photon simulator and then runs it. From there, the `qcrypto` binaries are run in order to process the resulting files and create matching final_key directories for the two parties. In Guardian, these files are seen by `notifier` which notifies `watcher` which reads them and puts the key content into the local Vault instance and deletes the final key files.

# Running a full QKD Setup

Instead of running the full qcrypto stack on one KME host, the processes would be separated by KME hosts. Let's assume that KME host 1 will serve the role of the Alice (A.K.A 'hec' or High Event Count) party. KME host 2 serve as the Bob (A.K.A or Low Event Count) party.

Here is a guess as to what you all would need to run:

### KME Host 1

* ../qcrypto/remotecrypto/transferd ...
* ../qcrypto/timestamp4/timestampper ...
* ../qcrypto/remotecrypto/chopper2 ...
* ../qcrypto/remotecrypto/getrate ...
* ../qcrypto/remotecrypto/pfind ...
* ../qcrypto/remotecrypto/costream ...
* ../qcrypto/errorcorrection/ecd2 ...

### KME Host 2

* ../qcrypto/remotecrypto/transferd ...
* ../qcrypto/timestamp4/timestampper ...
* ../qcrypto/remotecrypto/chopper ...
* ../qcrypto/remotecrypto/getrate ...
* ../qcrypto/remotecrypto/splicer ...
* ../qcrypto/errorcorrection/ecd2 ...


## Caveats

You all have the timestamp4 stuff. Integrate it in instead of the timestamp3 stuff.

I'll leave the command-line options to someone else! The `run_****` files might be of some help. They might also steer you wrong. When in doubt, go with Christian's defaults.

# Connecting to the Watcher Service

The error correction code will be outputting final key files into whatever directory you specify as well as sending notifications to a pipe using the `-l` option. This notification pipe should be made available to the `watcher` service:
```bash
### From the docker-compose.init.yml file, we see where the current docker volumes are mounted for KME host 1 and KME host 2:
  160     volumes:
  161       # NOTE: Only kme1 generates epoch files in this configuration
  162       - ./volumes/kme1/qkd/epoch_files/${LOCAL_KME_ID:-SETMEINMAKEFILE}:/epoch_files
```

The location of the produced final epoch files in the full setup are expected in the in-container directory of `/epoch_files` for watcher.
The notificate pipe is expected to be inside of this directory as `notify.pipe`; see `common/global_config: NOTIFY_PIPE_FILEPATH`.


## Other Thoughts

The `watcher` service is started, waits for notifications, and then is shutdown within the docker-compose.init.yml service stack. I would recommend moving it to the docker-compose.yml service stack so that it stays up and running along with the REST API. You could still start and stop it based on whatever you're doing with the QKD box and/or running the qcrypto stack.

I would create two new services for the qcrypto stack:
* qkd_hec (Alice)
* qkd_lec (Bob) or whatever

These are also put into the docker-compose.yml service stack and can be brought up and down using Docker commands/Makefile targets.

I would recommend keeping all command and control of the qcrypto service decoupled from outward-facing interfaces (REST API, Vault, etc.). I would start with displaying status information (if at all) first and then decide from a 'security' perspective what access (if any) should be in the same area as an SAE. I look at this a lot like a management plane / data plane type separation that the encryptor folks do. Airgapping is the simplest and likely most secure way of keeping malicious actors from having extra attack surfaces. It maybe harder because you don't have as many 'shiny things' for those who would fund you. Good luck!

On a different note, no need to keep such permissable files laying around.:
```bash
$ cat ${TOP_DIR}/qkd/qsim/run_copy
...
mkdir -p ./epoch_files/${out_dir}/
cp -a ${data_dir}/finalkey.${count_type}/* ./epoch_files/${out_dir}/

# NOTE (AKA Hack): These are only necessary when using rsync to remotely
# transfer epoch files instead of using a true QKD system.  These write
# permissions allow for convienent transfer and removal without need of a
# priviledged transfer service.
chmod 0777 ./epoch_files/${out_dir}/
chmod 0666 ./epoch_files/${out_dir}/*
```
When your epoch files quantumly appear instead of clumsily appearing via rsync, you don't have to worry about such things.
