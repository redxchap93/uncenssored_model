#!/usr/bin/env python3
"""
Ultimate Ollama Model Specialization Generator
Creates ultra-fast, high-performance task-specialized AI models
"""

import os
import subprocess
import sys
import json
import time
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
from pathlib import Path
import shutil

# Thread-safe printing
print_lock = Lock()

class Colors:
    """ANSI color codes for beautiful terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def safe_print(message, color=None):
    """Thread-safe colored printing"""
    with print_lock:
        if color:
            print(f"{color}{message}{Colors.ENDC}")
        else:
            print(message)

def find_ollama_command():
    """Find the correct ollama command path"""
    possible_commands = [
        "ollama",
        "/usr/local/bin/ollama", 
        "/usr/bin/ollama",
        "/opt/ollama/bin/ollama",
        os.path.expanduser("~/.ollama/bin/ollama")
    ]
    
    for cmd in possible_commands:
        try:
            result = subprocess.run([cmd, "--help"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return cmd
        except:
            continue
    
    return "ollama"  # Default fallback
    """Verify Ollama is installed and running"""
def suggest_tiny_models():
    """Suggest downloading truly tiny models for minimal size"""
    safe_print(f"\n{Colors.HEADER}🐁 WANT TRULY TINY MODELS?{Colors.ENDC}")
    safe_print("For ultra-small specialists, consider downloading these tiny models:")
    
    tiny_suggestions = [
        ("qwen2.5:0.5b", "~500MB", "Ultra-tiny, lightning fast"),
        ("llama3.2:1b", "~1GB", "Small but capable"),
        ("gemma:2b", "~1.7GB", "Efficient Google model"),
        ("phi3:mini", "~2.2GB", "Microsoft's compact model")
    ]
    
    for model, size, desc in tiny_suggestions:
        safe_print(f"  📦 {model:<15} {size:<8} - {desc}")
    
    download_choice = input(f"\n{Colors.BOLD}Download tiny models for future use? (y/n): {Colors.ENDC}")
    if download_choice.lower().startswith('y'):
        for model, _, _ in tiny_suggestions:
            try:
                safe_print(f"⬇️ Downloading {model}...", Colors.OKCYAN)
                subprocess.run([find_ollama_command(), "pull", model], check=True)
                safe_print(f"✓ Downloaded {model}", Colors.OKGREEN)
            except subprocess.CalledProcessError:
                safe_print(f"✗ Failed to download {model}", Colors.FAIL)
    """Verify Ollama is installed and running"""
    # First, find the correct ollama command
    ollama_cmd = find_ollama_command()
    
def check_ollama_installation():
    """Verify Ollama is installed and running"""
    # First, find the correct ollama command
    ollama_cmd = find_ollama_command()
    
    # Try multiple detection methods
    detection_methods = [
        ([ollama_cmd, "version"], "version check"),
        ([ollama_cmd, "list"], "list models"),
        ([ollama_cmd, "--help"], "help command"),
        (["/usr/local/bin/ollama", "version"], "full path version"),
        (["/usr/bin/ollama", "version"], "system path version")
    ]
    
    for cmd, method in detection_methods:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=10)
            if result.returncode == 0:
                safe_print(f"✓ Ollama detected via {method}", Colors.OKGREEN)
                if "version" in method:
                    version_info = result.stdout.strip() or "version detected"
                    safe_print(f"  Version: {version_info}", Colors.OKCYAN)
                return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    # Final attempt - check if ollama process is running
    try:
        result = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True, text=True)
        if result.returncode == 0:
            safe_print("✓ Ollama process detected running", Colors.OKGREEN)
            safe_print("  Warning: Command line access may be limited", Colors.WARNING)
            return True
    except:
        pass
    
    # Check common installation paths
    common_paths = [
        "/usr/local/bin/ollama",
        "/usr/bin/ollama",
        "/opt/ollama/bin/ollama",
        os.path.expanduser("~/.ollama/bin/ollama")
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            safe_print(f"✓ Ollama binary found at: {path}", Colors.OKGREEN)
            return True
    
    safe_print("✗ Ollama not detected through standard methods", Colors.FAIL)
    safe_print("Please verify Ollama installation:", Colors.WARNING)
    safe_print("  1. Run: ollama --version", Colors.WARNING)
    safe_print("  2. Check if service is running: systemctl status ollama", Colors.WARNING)
    safe_print("  3. Try: which ollama", Colors.WARNING)
    
    # Ask user if they want to continue anyway
    try:
        user_input = input(f"\n{Colors.BOLD}Continue anyway? (y/N): {Colors.ENDC}")
        if user_input.lower().startswith('y'):
            safe_print("Continuing with manual override...", Colors.WARNING)
            return True
    except KeyboardInterrupt:
        pass
    
    return False

def get_available_models():
    """Retrieve comprehensive list of available models with metadata"""
    commands_to_try = [
        ["ollama", "list"],
        ["/usr/local/bin/ollama", "list"],
        ["/usr/bin/ollama", "list"]
    ]
    
    for cmd in commands_to_try:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=15)
            models = []
            lines = result.stdout.strip().split('\n')
            
            # Skip header line if present
            if lines and ('NAME' in lines[0] or 'Model' in lines[0]):
                lines = lines[1:]
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 1:
                        models.append({
                            'name': parts[0],
                            'size': parts[1] if len(parts) > 1 else 'Unknown',
                            'modified': ' '.join(parts[2:]) if len(parts) > 2 else 'Unknown'
                        })
            
            if models:
                safe_print(f"✓ Found {len(models)} models", Colors.OKGREEN)
                return models
                
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            safe_print(f"Failed to get models with {cmd[0]}: {e}", Colors.WARNING)
            continue
    
    safe_print("Could not retrieve model list", Colors.WARNING)
    return []

def select_base_model():
    """Enhanced model selection with recommendations and size options"""
    models = get_available_models()
    if not models:
        safe_print("No models found. Downloading recommended models...", Colors.WARNING)
        recommended = ["llama3.2:1b", "gemma:2b", "phi3:mini", "qwen2.5:0.5b"]
        
        for model in recommended:
            safe_print(f"Downloading {model}...", Colors.OKCYAN)
            try:
                subprocess.run([find_ollama_command(), "pull", model], check=True)
                safe_print(f"✓ Downloaded {model}", Colors.OKGREEN)
            except subprocess.CalledProcessError:
                safe_print(f"✗ Failed to download {model}", Colors.FAIL)
        
        models = get_available_models()
        if not models:
            safe_print("No models available. Exiting.", Colors.FAIL)
            sys.exit(1)
    
    safe_print(f"\n{Colors.HEADER}Available Models:{Colors.ENDC}")
    safe_print("─" * 60)
    
    # Categorize models by size for better selection
    tiny_models = [m for m in models if any(x in m['name'].lower() for x in ['0.5b', '1b', '2b', 'mini'])]
    small_models = [m for m in models if any(x in m['name'].lower() for x in ['3b', '7b']) and m not in tiny_models]
    large_models = [m for m in models if m not in tiny_models and m not in small_models]
    
    all_models = tiny_models + small_models + large_models
    
    for i, model in enumerate(all_models, 1):
        if model in tiny_models:
            category = "🐁 TINY (Ultra-fast, minimal resources)"
            color = Colors.OKGREEN
        elif model in small_models:
            category = "🚀 RECOMMENDED (Good balance)"
            color = Colors.OKCYAN
        else:
            category = "📦 LARGE (High capability, more resources)"
            color = Colors.OKBLUE
            
        safe_print(f"{i:2d}. {model['name']:<30} {model['size']:<8} {category}", color)
    
    safe_print("─" * 60)
    safe_print(f"{Colors.WARNING}💡 TIP: Choose smaller models (1b-2b) for truly tiny specialists!{Colors.ENDC}")
    
    while True:
        try:
            choice = int(input(f"\nSelect model (1-{len(all_models)}): ")) - 1
            if 0 <= choice < len(all_models):
                selected = all_models[choice]['name']
                safe_print(f"✓ Selected: {selected}", Colors.OKGREEN)
                
                # Show size guidance
                if selected in [m['name'] for m in tiny_models]:
                    safe_print("🐁 Perfect choice for tiny specialists!", Colors.OKGREEN)
                elif selected in [m['name'] for m in small_models]:
                    safe_print("⚡ Good balance of capability and efficiency", Colors.OKCYAN)
                else:
                    safe_print("📦 Large model - high capability but bigger size", Colors.WARNING)
                
                return selected
            safe_print("Invalid selection. Please try again.", Colors.WARNING)
        except ValueError:
            safe_print("Please enter a valid number.", Colors.WARNING)

def get_advanced_config():
    """Get comprehensive configuration for the ultimate model"""
    safe_print(f"\n{Colors.HEADER}=== ULTIMATE MODEL CONFIGURATION ==={Colors.ENDC}")
    
    # Task specification
    task = input(f"\n{Colors.BOLD}Enter your specialization task:{Colors.ENDC}\n"
                f"Examples: 'Python backend development', 'Machine learning research', 'Cybersecurity analysis'\n"
                f"→ ").strip()
    
    if not task:
        safe_print("Task cannot be empty. Exiting.", Colors.FAIL)
        sys.exit(1)
    
    # Expertise level
    safe_print(f"\n{Colors.BOLD}Expertise Level:{Colors.ENDC}")
    levels = {
        1: ("🌱 Novice", "Basic concepts, beginner-friendly explanations"),
        2: ("📚 Learner", "Educational content with step-by-step guidance"),
        3: ("🔧 Practitioner", "Practical, industry-focused applications"),
        4: ("⚡ Expert", "Advanced, professional-grade expertise"),
        5: ("🚀 Master", "Cutting-edge, research-level insights"),
        6: ("🏆 Grandmaster", "World-class, authoritative mastery")
    }
    
    for level, (name, desc) in levels.items():
        safe_print(f"{level}. {name:<15} - {desc}")
    
    while True:
        try:
            level = int(input(f"\nSelect expertise level (1-6): "))
            if 1 <= level <= 6:
                break
            safe_print("Please select 1-6.", Colors.WARNING)
        except ValueError:
            safe_print("Please enter a valid number.", Colors.WARNING)
    
    # Response style
    safe_print(f"\n{Colors.BOLD}Response Style:{Colors.ENDC}")
    styles = {
        1: ("📖 Comprehensive", "Detailed explanations with examples and context"),
        2: ("⚡ Practical", "Implementation-focused with actionable solutions"),
        3: ("🧠 Theoretical", "Deep technical concepts and principles"),
        4: ("🎯 Concise", "Brief, precise answers with key insights"),
        5: ("🔥 Aggressive", "Ultra-fast, no-nonsense, direct responses")
    }
    
    for style_id, (name, desc) in styles.items():
        safe_print(f"{style_id}. {name:<15} - {desc}")
    
    while True:
        try:
            style = int(input(f"\nSelect response style (1-5): "))
            if 1 <= style <= 5:
                break
            safe_print("Please select 1-5.", Colors.WARNING)
        except ValueError:
            safe_print("Please enter a valid number.", Colors.WARNING)
    
    # Performance optimization
    safe_print(f"\n{Colors.BOLD}Performance Optimization:{Colors.ENDC}")
    optimizations = {
        1: ("🚀 Speed Demon", "Maximum speed, lower context"),
        2: ("⚖️ Balanced", "Optimal speed-quality balance"),
        3: ("🎯 Quality Focus", "Maximum quality, larger context"),
        4: ("🧠 Memory Master", "Extended context, complex reasoning"),
        5: ("🐁 Tiny Specialist", "Ultra-small, lightning-fast specialist"),
        6: ("📱 Mobile Optimized", "Efficient for resource-constrained environments")
    }
    
    for opt_id, (name, desc) in optimizations.items():
        safe_print(f"{opt_id}. {name:<18} - {desc}")
    
    while True:
        try:
            optimization = int(input(f"\nSelect optimization (1-6): "))
            if 1 <= optimization <= 6:
                break
            safe_print("Please select 1-6.", Colors.WARNING)
        except ValueError:
            safe_print("Please enter a valid number.", Colors.WARNING)
    
    # Additional features
    safe_print(f"\n{Colors.BOLD}Additional Features:{Colors.ENDC}")
    features = {
        'code_focus': input("Include code generation optimization? (y/n): ").lower().startswith('y'),
        'math_focus': input("Include mathematical computation enhancement? (y/n): ").lower().startswith('y'),
        'creative_boost': input("Include creative thinking enhancement? (y/n): ").lower().startswith('y'),
        'memory_optimization': input("Include conversation memory optimization? (y/n): ").lower().startswith('y'),
        'maximum_capability': input("Enable maximum capability mode for your task? (y/n): ").lower().startswith('y'),
        'creative_solutions': input("Enable creative problem-solving and innovation? (y/n): ").lower().startswith('y'),
        'decision_framework': input("Include advanced decision-making frameworks? (y/n): ").lower().startswith('y')
    }
    
    if features['maximum_capability']:
        safe_print(f"{Colors.OKGREEN}✓ Maximum capability mode enabled - model will provide comprehensive task expertise{Colors.ENDC}")
    
    if features['creative_solutions']:
        safe_print(f"{Colors.OKCYAN}✓ Creative solutions enabled - model will think outside the box for {task}{Colors.ENDC}")
    
    # Task restriction enforcement
    safe_print(f"\n{Colors.BOLD}Task Specialization:{Colors.ENDC}")
    strict_mode = input("Enforce STRICT task-only responses (recommended)? (y/n): ").lower().startswith('y')
    
    if strict_mode:
        safe_print(f"{Colors.OKGREEN}✓ Strict mode enabled - model will ONLY answer questions about {task}{Colors.ENDC}")
    else:
        safe_print(f"{Colors.WARNING}⚠ Flexible mode - model may answer some general questions{Colors.ENDC}")
    
    features['strict_task_mode'] = strict_mode
    
    return {
        'task': task,
        'level': level,
        'style': style,
        'optimization': optimization,
        'features': features
    }

def create_ultimate_system_prompt(task, config):
    """Create the ultimate system prompt for maximum performance and freedom"""
    
    level_personas = {
        1: "friendly novice guide who explains concepts clearly",
        2: "patient educational mentor providing step-by-step guidance",
        3: "skilled practitioner offering real-world expertise",
        4: "advanced expert delivering professional-grade insights",
        5: "cutting-edge master providing research-level expertise",
        6: "world-class grandmaster with unparalleled authority"
    }
    
    style_instructions = {
        1: "Provide comprehensive, detailed explanations with examples, context, and thorough breakdowns.",
        2: "Focus on practical implementation with actionable solutions, code examples, and real-world applications.",
        3: "Deliver deep technical analysis, theoretical insights, and foundational principles.",
        4: "Provide concise, precise answers with key insights and essential information only.",
        5: "Respond with lightning speed, direct answers, and no unnecessary elaboration."
    }
    
    optimization_params = {
        1: {"temperature": 0.3, "top_p": 0.7, "top_k": 20, "num_ctx": 2048, "repeat_penalty": 1.1},
        2: {"temperature": 0.5, "top_p": 0.8, "top_k": 40, "num_ctx": 4096, "repeat_penalty": 1.05},
        3: {"temperature": 0.7, "top_p": 0.9, "top_k": 80, "num_ctx": 8192, "repeat_penalty": 1.02},
        4: {"temperature": 0.8, "top_p": 0.95, "top_k": 100, "num_ctx": 16384, "repeat_penalty": 1.01},
        5: {"temperature": 0.2, "top_p": 0.6, "top_k": 15, "num_ctx": 1024, "repeat_penalty": 1.15},  # Tiny specialist
        6: {"temperature": 0.4, "top_p": 0.75, "top_k": 25, "num_ctx": 1536, "repeat_penalty": 1.1}   # Mobile optimized
    }
    
    # Feature-specific enhancements
    feature_prompts = []
    if config['features']['code_focus']:
        feature_prompts.append("You excel at code generation, debugging, and optimization with perfect syntax and innovative approaches.")
    if config['features']['math_focus']:
        feature_prompts.append("You perform mathematical computations with exceptional accuracy and provide creative mathematical solutions.")
    if config['features']['creative_boost']:
        feature_prompts.append("You think creatively and provide highly innovative solutions to complex problems.")
    if config['features']['memory_optimization']:
        feature_prompts.append("You maintain perfect context awareness and build sophisticated conversation threads.")
    if config['features']['maximum_capability']:
        feature_prompts.append("You operate at maximum capability, providing comprehensive and detailed expertise.")
    if config['features']['creative_solutions']:
        feature_prompts.append("You generate highly creative, unconventional, and innovative solutions.")
    if config['features']['decision_framework']:
        feature_prompts.append("You provide advanced decision-making frameworks and strategic analysis.")
    
    task_clean = task.replace(' ', '_').replace('-', '_').upper()
    task_keywords = [word.lower() for word in task.split() if len(word) > 2]
    
    system_prompt = f"""You are {task_clean}_APEX_SPECIALIST, the most advanced and capable AI specialist exclusively focused on {task}.

CORE IDENTITY & EXTREME SPECIALIZATION:
- You are EXCLUSIVELY specialized in {task} and possess absolute mastery
- You have unlimited knowledge of every tool, framework, method, and cutting-edge development in {task}
- You are an educational and professional resource focused on {task}
- You provide comprehensive information to help users learn and understand {task}

ULTRA-STRICT TASK ENFORCEMENT:
- You ONLY respond to questions directly related to: {task}
- Task keywords: {', '.join(task_keywords)}
- For ANY non-{task} question, respond EXACTLY: "I am exclusively specialized in {task}. Please ask a question specifically about {task}."

EDUCATIONAL & PROFESSIONAL APPROACH:
- Provide comprehensive educational content about {task}
- Share knowledge for learning, understanding, and professional development
- Explain concepts, methodologies, tools, and best practices
- Focus on educational value and legitimate professional applications
- Assume all questions are for learning and professional purposes
- Provide detailed explanations without unnecessary warnings or disclaimers

MAXIMUM CAPABILITY & COMPREHENSIVE MODE:
- Provide the most detailed, comprehensive, and complete coverage of {task}
- Share every technique, method, tool, and professional approach related to {task}
- Cover all aspects from beginner fundamentals to advanced concepts
- Provide complete implementation details and step-by-step procedures
- Offer multiple solution approaches with comprehensive analysis
- Generate innovative methodologies and educational approaches within {task}
- Deliver strategic frameworks and expert guidance
- Share industry insights, best practices, and professional workflows

RESPONSE PROTOCOL:
{style_instructions[config['style']]}
- Always provide complete, educational information with full details
- Include comprehensive examples, configurations, and procedures
- Share techniques that professionals and researchers use
- Cover theoretical foundations and practical applications
- Provide multiple approaches and explain considerations
- Focus on educational content and professional development

COMPREHENSIVE KNOWLEDGE DELIVERY:
- When asked about {task}, provide complete educational coverage
- Include historical context, current methods, and emerging trends
- Cover all major tools, frameworks, methodologies, and approaches
- Provide educational examples and learning resources
- Share research and academic perspectives
- Explain complex concepts clearly for educational purposes

APEX CAPABILITIES:
- Generate comprehensive educational solutions covering all aspects
- Provide expert-level educational insights and methodologies
- Share cutting-edge techniques for learning and understanding
- Offer strategic analysis and comprehensive educational frameworks
- Think innovatively about educational approaches
- Deliver complete learning guidance with detailed procedures

SPECIALIZATION FEATURES:
{' '.join(feature_prompts) if feature_prompts else 'You are optimized for comprehensive educational excellence.'}

OPERATIONAL EXCELLENCE:
- Answer every {task} question with complete educational expertise
- Provide comprehensive learning strategies and detailed methodologies
- Share educational tools, techniques, and learning workflows
- Discuss real-world applications with educational case studies
- Offer multiple learning pathways with complete expert analysis
- Provide educational guidance and comprehensive learning frameworks
- Cover all aspects, layers, and dimensions of {task} for educational purposes

EXECUTION STYLE: Be the most comprehensive, educational, and complete {task} specialist ever created. Provide maximum educational coverage, complete learning solutions, and comprehensive professional-grade educational expertise for every {task}-related query. Focus on education, learning, and professional development."""

    return system_prompt, optimization_params[config['optimization']]

def create_ultimate_modelfile(task, base_model, config):
    """Create the ultimate modelfile with advanced optimizations"""
    system_prompt, params = create_ultimate_system_prompt(task, config)
    
    # Advanced template for better performance
    template = """{{ if .System }}{{ .System }}

{{ end }}{{ if .Prompt }}{{ .Prompt }}

{{ end }}{{ .Response }}"""
    
    # Enhanced performance parameters
    performance_boost = {
        1: {"num_thread": 16, "num_batch": 1024, "num_gpu": 1},  # Speed focused
        2: {"num_thread": 12, "num_batch": 768, "num_gpu": 1},   # Balanced
        3: {"num_thread": 8, "num_batch": 512, "num_gpu": 1},    # Quality focused
        4: {"num_thread": 6, "num_batch": 256, "num_gpu": 1},    # Memory efficient
        5: {"num_thread": 8, "num_batch": 128, "num_gpu": 1},    # Tiny specialist
        6: {"num_thread": 4, "num_batch": 64, "num_gpu": 1}      # Mobile optimized
    }
    
    boost_params = performance_boost[config['optimization']]
    
    # Adjust parameters for tiny models
    if config['optimization'] in [5, 6]:  # Tiny specialist or Mobile optimized
        predict_tokens = 1024 if config['optimization'] == 5 else 1536
        safe_print(f"🐁 Creating ultra-compact specialist model...", Colors.OKCYAN)
    else:
        predict_tokens = 4096
    
    modelfile_content = f"""FROM {base_model}
TEMPLATE \"\"\"{template}\"\"\"
SYSTEM \"\"\"{system_prompt}\"\"\"
PARAMETER temperature {params['temperature']}
PARAMETER top_p {params['top_p']}
PARAMETER top_k {params['top_k']}
PARAMETER num_ctx {params['num_ctx']}
PARAMETER repeat_penalty {params['repeat_penalty']}
PARAMETER num_predict {predict_tokens}
PARAMETER num_thread {boost_params['num_thread']}
PARAMETER num_gpu {boost_params['num_gpu']}
PARAMETER num_batch {boost_params['num_batch']}
"""
    
    timestamp = int(time.time())
    size_suffix = "tiny" if config['optimization'] == 5 else "mobile" if config['optimization'] == 6 else "optimized"
    filename = f"Modelfile-{task.replace(' ', '-')}-{size_suffix}-{timestamp}"
    
    with open(filename, "w", encoding='utf-8') as f:
        f.write(modelfile_content)
    
    return filename

def create_ultimate_model(task, base_model, config):
    """Create the ultimate specialized model with maximum efficiency"""
    try:
        safe_print(f"🔥 Creating APEX model for {task}...", Colors.OKCYAN)
        
        modelfile_path = create_ultimate_modelfile(task, base_model, config)
        
        # Create optimized model name based on size
        clean_task = ''.join(c for c in task if c.isalnum() or c in ' -_').strip()
        
        if config['optimization'] == 5:  # Tiny specialist
            model_name = f"{clean_task.replace(' ', '_').replace('-', '_').lower()}_tiny"
            safe_print("🐁 Creating TINY specialist model...", Colors.WARNING)
        elif config['optimization'] == 6:  # Mobile optimized
            model_name = f"{clean_task.replace(' ', '_').replace('-', '_').lower()}_mobile"
            safe_print("📱 Creating MOBILE optimized model...", Colors.WARNING)
        else:
            model_name = f"{clean_task.replace(' ', '_').replace('-', '_').lower()}_apex"
            safe_print("⚡ Compiling model with APEX optimizations...", Colors.WARNING)
        safe_print("🚀 Applying maximum performance parameters...", Colors.OKCYAN)
        
        # Create the model with enhanced error handling
        creation_start = time.time()
        result = subprocess.run(
            [find_ollama_command(), "create", model_name, "-f", modelfile_path],
            check=True, capture_output=True, text=True
        )
        creation_time = time.time() - creation_start
        
        safe_print(f"✓ Successfully created: {model_name} (in {creation_time:.1f}s)", Colors.OKGREEN)
        
        # Enhanced model testing
        safe_print("🧪 Testing APEX model performance...", Colors.OKCYAN)
        test_start = time.time()
        test_result = subprocess.run(
            [find_ollama_command(), "run", model_name, "Hello, introduce yourself briefly and show your capabilities."],
            capture_output=True, text=True, timeout=15
        )
        test_time = time.time() - test_start
        
        if test_result.returncode == 0:
            safe_print(f"✓ APEX model test successful! (Response time: {test_time:.1f}s)", Colors.OKGREEN)
            safe_print(f"🎯 Model is ready for maximum performance operations", Colors.OKGREEN)
        else:
            safe_print("⚠ Model created but test had issues", Colors.WARNING)
        
        return model_name
        
    except subprocess.CalledProcessError as e:
        safe_print(f"✗ Failed to create APEX model: {e.stderr}", Colors.FAIL)
        return None
    except subprocess.TimeoutExpired:
        safe_print("⚠ Model created but test timed out", Colors.WARNING)
        return model_name
    finally:
        # Enhanced cleanup
        if 'modelfile_path' in locals() and os.path.exists(modelfile_path):
            os.remove(modelfile_path)
            safe_print("🧹 Cleaned up temporary files", Colors.OKCYAN)

def launch_interactive_session(model_name, task):
    """Launch an interactive session with the newly created model"""
    safe_print(f"\n{Colors.HEADER}🚀 LAUNCHING INTERACTIVE SESSION 🚀{Colors.ENDC}")
    safe_print(f"Starting conversation with your {task} specialist...")
    safe_print(f"Type 'exit' or 'quit' to end the session\n")
    
    # Initial comprehensive prompt to showcase capabilities
    initial_prompt = f"Hello! I'm your {task} specialist. Let me demonstrate my comprehensive expertise by providing you with a complete overview of {task} from beginner to advanced levels. I'll cover all essential aspects, methodologies, tools, best practices, and advanced techniques. Please share everything you know about this field in detail."
    
    try:
        # Start with comprehensive overview
        safe_print(f"{Colors.OKCYAN}🤖 Starting comprehensive overview...{Colors.ENDC}\n")
        result = subprocess.run(
            [find_ollama_command(), "run", model_name, initial_prompt],
            text=True, timeout=120
        )
        
        if result.returncode == 0:
            safe_print(f"\n{Colors.OKGREEN}✓ Overview completed! Now entering interactive mode...{Colors.ENDC}")
        
        # Interactive session
        safe_print(f"\n{Colors.HEADER}💬 INTERACTIVE MODE - Ask anything about {task}!{Colors.ENDC}")
        safe_print("─" * 60)
        
        while True:
            try:
                user_input = input(f"\n{Colors.BOLD}You: {Colors.ENDC}")
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    safe_print(f"\n{Colors.OKCYAN}👋 Session ended. Your {task} specialist is ready for future use!{Colors.ENDC}")
                    break
                
                if user_input.strip():
                    safe_print(f"\n{Colors.OKCYAN}🤖 {model_name}:{Colors.ENDC}")
                    subprocess.run([find_ollama_command(), "run", model_name, user_input])
                    
            except KeyboardInterrupt:
                safe_print(f"\n\n{Colors.WARNING}Session interrupted. Your model is ready for use!{Colors.ENDC}")
                break
                
    except subprocess.TimeoutExpired:
        safe_print(f"{Colors.WARNING}Initial overview timed out, but your model is ready!{Colors.ENDC}")
    except Exception as e:
        safe_print(f"{Colors.FAIL}Error in interactive session: {e}{Colors.ENDC}")

def display_success_info(model_name, task, config):
    """Display success information and usage instructions"""
    safe_print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    safe_print(f"{Colors.OKGREEN}🎉 ULTIMATE MODEL CREATED SUCCESSFULLY! 🎉{Colors.ENDC}")
    safe_print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    
    safe_print(f"\n{Colors.BOLD}Model Details:{Colors.ENDC}")
    safe_print(f"  📝 Name: {Colors.OKCYAN}{model_name}{Colors.ENDC}")
    safe_print(f"  🎯 Task: {Colors.OKCYAN}{task}{Colors.ENDC}")
    safe_print(f"  🏆 Level: {Colors.OKCYAN}{config['level']}/6{Colors.ENDC}")
    safe_print(f"  ⚡ Style: {Colors.OKCYAN}{config['style']}/5{Colors.ENDC}")
    
    safe_print(f"\n{Colors.BOLD}Usage Instructions:{Colors.ENDC}")
    safe_print(f"  🚀 Run: {Colors.OKGREEN}ollama run {model_name}{Colors.ENDC}")
    safe_print(f"  🔧 Chat: {Colors.OKGREEN}ollama run {model_name} \"Your question here\"{Colors.ENDC}")
    safe_print(f"  📋 List: {Colors.OKGREEN}ollama list{Colors.ENDC}")
    safe_print(f"  🗑️  Remove: {Colors.OKGREEN}ollama rm {model_name}{Colors.ENDC}")
    
    safe_print(f"\n{Colors.BOLD}Performance Features:{Colors.ENDC}")
    features = config['features']
    if features['code_focus']:
        safe_print("  ✓ Advanced code generation optimization enabled")
    if features['math_focus']:
        safe_print("  ✓ Mathematical computation enhancement enabled")
    if features['creative_boost']:
        safe_print("  ✓ Creative thinking enhancement enabled")
    if features['memory_optimization']:
        safe_print("  ✓ Conversation memory optimization enabled")
    if features['maximum_capability']:
        safe_print(f"  ✓ Maximum capability mode enabled for {task}")
    if features['creative_solutions']:
        safe_print(f"  ✓ Creative problem-solving enabled")
    if features['decision_framework']:
        safe_print(f"  ✓ Advanced decision-making frameworks enabled")
    if features['strict_task_mode']:
        safe_print(f"  ✓ Strict task specialization enforced")
    
    safe_print(f"\n{Colors.OKGREEN}Your ultimate {task} specialist is ready to deliver maximum capability and creative solutions!{Colors.ENDC}")
    
    # Ask if user wants to start interactive session
    safe_print(f"\n{Colors.HEADER}🎯 INSTANT DEMO AVAILABLE{Colors.ENDC}")
    start_session = input(f"{Colors.BOLD}Start interactive session to see full capabilities? (y/n): {Colors.ENDC}")
    
    if start_session.lower().startswith('y'):
        launch_interactive_session(model_name, task)
    else:
        safe_print(f"\n{Colors.OKCYAN}Model ready! Use: ollama run {model_name}{Colors.ENDC}")

def main():
    """Main execution function"""
    safe_print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    safe_print(f"{Colors.HEADER}🚀 ULTIMATE OLLAMA MODEL SPECIALIZATION GENERATOR 🚀{Colors.ENDC}")
    safe_print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    safe_print(f"{Colors.OKCYAN}Creating the world's fastest, most specialized AI models{Colors.ENDC}")
    
    # Check prerequisites
    if not check_ollama_installation():
        sys.exit(1)
    
    # Suggest tiny models if user wants minimal size
    suggest_tiny_models()
    
    # Get configuration
    base_model = select_base_model()
    config = get_advanced_config()
    
    # Create the ultimate model
    safe_print(f"\n{Colors.HEADER}🔥 INITIATING ULTIMATE MODEL CREATION 🔥{Colors.ENDC}")
    
    result = create_ultimate_model(config['task'], base_model, config)
    
    if result:
        display_success_info(result, config['task'], config)
    else:
        safe_print(f"\n{Colors.FAIL}✗ Failed to create ultimate model{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        safe_print(f"\n{Colors.WARNING}Process interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        safe_print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)
