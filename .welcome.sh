#!/usr/bin/env bash

# ANSI Color Codes
CYAN='\033[1;36m'
MAGENTA='\033[1;35m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
BOLD='\033[1m'
NC='\033[0m'

clear

# 1. 2D Anatomical ASCII Brain (Clean Escaping)
echo -e "${MAGENTA}                 ___    ___${NC}"
echo -e "${MAGENTA}            ..\"\`)\" \`..\" \`(\`\`..${NC}"
echo -e "${MAGENTA}          .'; _..=. :: \`-'.' ;\`."
echo -e "${MAGENTA}         : ) ;\"\`':._::_.      ( :.${NC}"
echo -e "${MAGENTA}       .:-\"   _.  \`\"${WHITE}##${MAGENTA}\"\` \"._   \`-:\\\\${NC}"
echo -e "${CYAN}      /.\"   -\"\`  ._.::._. .'\"-   \".:${NC}"
echo -e "${CYAN}     : :    ( -: \`\" :: \"\` :- )    : )${NC}"
echo -e "${CYAN}    ( .\":==._' \`'=._${WHITE}##${CYAN}_.='\` '_.==: .'${NC}"
echo -e "${CYAN}    (:  \`, \`\"\`    \`\"${WHITE}##${CYAN}\"\`    \`\"\` .'\`\".)${NC}"
echo -e "${CYAN}     \\\`'  \`\"--.  \"- )( -\" ..--\"\`  \`-/${NC}"
echo -e "${CYAN}     (\" (_.\" =\"\"-...\"\`...-\"\"= \"._) \")"
echo -e "${YELLOW}      \"..__..-\"  )%${WHITE}\`..'%${YELLOW}(  \"-..__..\"${NC}"
echo -e "${YELLOW}           (#\"...'\\\\${WHITE}%%%%${YELLOW}/\`...\"#)${NC}"
echo -e "${YELLOW}            \`######\`--'######\"${NC}"
echo -e "${GREEN}              \"###\")@@(\`###\"${NC}"
echo -e "${GREEN}                   \\@@/${NC}"
echo -e "${GREEN}                    )(        ${GRAY}rscr${NC}"
echo ""

# 2. System & Hardware Telemetry
PY_VER=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))" 2>/dev/null || echo "3.12")
CUDA_STATUS=$(python3 -c "import torch; print('CUDA Ready' if torch.cuda.is_available() else 'CPU Mode')" 2>/dev/null || echo "CPU Mode")
RAM_USAGE=$(free -h | awk '/Mem:/ {print $3 "/" $2}')
TOTAL_MODELS=$(find ~/neuro-lab -maxdepth 2 -type f -name "*.py" ! -name ".welcome.sh" ! -name "sim.py" 2>/dev/null | wc -l)
TOTAL_NOTEBOOKS=$(find ~/neuro-lab -maxdepth 2 -type f -name "*.ipynb" 2>/dev/null | wc -l)

# 3. Daily Computational Neuroscience Concept (Rotates Daily)
CONCEPTS=(
  "Leaky Integrate-and-Fire :: tau_m * dV/dt = -(V - V_rest) + R*I(t) | Basic membrane RC charging"
  "Hodgkin-Huxley Na+ Gating :: I_Na = g_Na * m^3 * h * (V - E_Na)    | Transient depolarizing spike upstroke"
  "Nernst Potential Formula  :: E_ion = (RT / zF) * ln([out]/[in])    | Electrochemical ionic equilibrium"
  "STDP Plasticity Rule      :: Delta_w = A+ * exp(-dt/tau+)          | Temporal Hebbian synaptic learning"
  "Cable Theory Length Const :: lambda = sqrt((r_m / r_i))            | Spatial electrotonic signal decay"
  "Izhikevich Simple Model   :: dv/dt = 0.04*v^2 + 5*v + 140 - u + I  | 2-variable rich spiking dynamics"
)
DAY_INDEX=$(($(date +%-j) % ${#CONCEPTS[@]}))
TODAYS_CONCEPT="${CONCEPTS[$DAY_INDEX]}"

echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║${NC}               ${WHITE}N E U R O - L A B   //   A R C H   L I N U X${NC}                 ${MAGENTA}║${NC}"
echo -e "${MAGENTA}╠═══════════════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${MAGENTA}║${NC}  [•] Workspace : ~/neuro-lab             [•] Python  : v${PY_VER} (Virtualenv)   ${MAGENTA}║${NC}"
echo -e "${MAGENTA}║${NC}  [•] Compute   : ${GREEN}${CUDA_STATUS}${NC}               [•] RAM     : ${RAM_USAGE}        ${MAGENTA}║${NC}"
echo -e "${MAGENTA}║${NC}  [•] Models    : ${WHITE}${TOTAL_MODELS} scripts / ${TOTAL_NOTEBOOKS} notebooks${NC}  [•] Compositor: Hyprland / Wayland   ${MAGENTA}║${NC}"
echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}─── DAILY NEUROSCIENCE FOUNDATION ──────────────────────────────────────────${NC}"
echo -e " ${YELLOW}⚡ ${WHITE}${TODAYS_CONCEPT}${NC}"
echo ""

echo -e "${CYAN}─── ACTIVE TOOLCHAIN ───────────────────────────────────────────────────────${NC}"
echo -e " ${GREEN}✔${NC} ${WHITE}Brian 2${NC}       ${GRAY}(ODE point biophysics)${NC}     ${GREEN}✔${NC} ${WHITE}snnTorch${NC}     ${GRAY}(SNNs & BPTT)${NC}"
echo -e " ${GREEN}✔${NC} ${WHITE}NEURON${NC}        ${GRAY}(3D cable morphology)${NC}      ${GREEN}✔${NC} ${WHITE}Elephant/Neo${NC} ${GRAY}(Electrophysiology)${NC}"
echo -e " ${GREEN}✔${NC} ${WHITE}Nengo & GUI${NC}   ${GRAY}(Cognitive architectures)${NC}"
echo ""

echo -e "${CYAN}─── INTERACTIVE LAUNCHER ───────────────────────────────────────────────────${NC}"
echo -e " [${YELLOW}1${NC}] Launch Nengo GUI (Browser)        [${YELLOW}3${NC}] Run Terminal LIF Spike Simulation"
echo -e " [${YELLOW}2${NC}] Launch JupyterLab Workspace       [${YELLOW}Enter${NC}] Return to Shell"
echo -e "${GRAY}────────────────────────────────────────────────────────────────────────────${NC}"
echo -n -e "${BOLD}Select action [1-3 / Enter]: ${NC}"

read -r -t 8 ACTION # Waits 8 seconds, then drops to normal terminal prompt
case "$ACTION" in
    1)
        echo -e "\n${GREEN}Starting Nengo GUI on http://localhost:8080...${NC}"
        nengo
        ;;
    2)
        echo -e "\n${GREEN}Starting JupyterLab...${NC}"
        jupyter lab
        ;;
    3)
        echo -e "\n${GREEN}Simulating Leaky Integrate-and-Fire neuron...${NC}"
        python3 ~/neuro-lab/sim.py
        ;;
    *)
        echo ""
        ;;
esac
