{
  "project_metadata": {
    "name": "God Mode Scaffolder",
    "version": "0.2.1",
    "codename": "Waddler OS",
    "developer": "Carter the Duck Developer",
    "license": "MIT",
    "intended_for": "bilbywilby",
    "last_updated": "2026-07-08T17:25:00Z",
    "description": "An AI-ready Python project bootstrapper creating production-ready scaffolding with security hooks, CI/CD pipelines, and token-optimized architectures for Claude and other LLM interfaces."
  },
  "core_philosophy": {
    "cross_platform_reliability": "Pure Python implementation replacing brittle shell scripts, ensuring safety and standard execution across Chromebooks (Crostini), macOS, Linux, and Windows.",
    "token_efficiency": "Strict enforcement of local runspaces and automatic `.claudeignore` injection to prevent AI tools from wasting expensive prompt context on build artifacts and system files.",
    "automated_hygiene": "Zero-trust commit safety via global and local Git templates that actively scan for accidental secret leaks, broken syntax, and trailing whitespace errors."
  },
  "system_prerequisites": {
    "python_version": ">=3.7",
    "required_packages": [
      "argparse",
      "subprocess",
      "pathlib",
      "shutil"
    ],
    "external_tools": {
      "git": "Required for repository initialization, configuration, and hook deployment.",
      "python3-venv": "Required for creating virtual environments in generated scaffolds."
    }
  },
  "architectural_components": {
    "hatch_py": {
      "purpose": "The central engine responsible for parsing arguments, creating clean directory structures, writing boilerplate code, and configuring Git structures.",
      "entry_point": "hatch.py",
      "cli_interface": {
        "arguments": {
          "project_name": "Optional. Name of the directory to be created for a new project.",
          "base_path": "Optional. Custom parent directory for project generation (defaults to current working directory)."
        },
        "flags": {
          "-t, --template": "Choices: ['cli', 'web', 'lib']. Configures directory layouts and standard boilerplates.",
          "--setup-global": "Configures a system-wide Git template directory to automate hooks for all future projects."
        }
      }
    }
  },
  "template_engine_details": {
    "cli": {
      "name": "Command Line Interface",
      "primary_use": "Standard utility programs and scripts.",
      "directories": ["src", "tests", "docs", "scripts", ".github/workflows"],
      "files_generated": [
        "src/main.py (argparse, logging boilerplate)",
        "tests/test_main.py (basic placeholder test)"
      ],
      "extra_dependencies": []
    },
    "web": {
      "name": "FastAPI Web Application",
      "primary_use": "Asynchronous microservices, backend APIs, and web services.",
      "directories": [
        "src", "src/api", "src/core", "src/static",
        "tests", "docs", "scripts", ".github/workflows"
      ],
      "files_generated": [
        "src/main.py (FastAPI app router bootstrap)",
        "src/api/router.py (base API endpoints blueprint)",
        "tests/test_main.py (FastAPI TestClient integration check)"
      ],
      "extra_dependencies": [
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.22.0"
      ]
    },
    "lib": {
      "name": "Python Package/Library",
      "primary_use": "Reusable utility code meant for distribution.",
      "directories": ["src", "src/{package_name}", "tests", "docs", "scripts", ".github/workflows"],
      "files_generated": [
        "src/{package_name}/__init__.py (version & metadata declarations)",
        "src/{package_name}/core.py (base math function logic placeholder)",
        "tests/test_core.py (pytest core utility check)"
      ],
      "extra_dependencies": [
        "setuptools>=68.0.0",
        "wheel>=0.40.0"
      ]
    }
  },
  "security_and_quality_guardrails": {
    "git_pre_commit_hooks": {
      "location_local": "{project_name}/.git/hooks/pre-commit",
      "location_global": "~/.git-templates/hooks/pre-commit",
      "validations": [
        {
          "check_name": "Accidental Secret Detection",
          "pattern": "(ANTHROPIC_API_KEY|github_token|password|secret|DATABASE_URL)",
          "severity": "CRITICAL (Blocks commit)",
          "error_msg": "QUACK! Secret detected in staged changes!"
        },
        {
          "check_name": "Python Syntax Validation",
          "command": "python3 -m py_compile",
          "severity": "HIGH (Blocks commit)",
          "error_msg": "Fails if syntax errors are present in any staged .py file."
        },
        {
          "check_name": "Trailing Whitespace Prevention",
          "pattern": "^\\\\+.*[[:space:]]$",
          "severity": "WARNING (Blocks commit to ensure pristine git diffs)",
          "error_msg": "Trailing whitespace detected!"
        }
      ]
    },
    "git_commit_template": {
      "location_local": "{project_name}/.gitmessage",
      "location_global": "~/.gitmessage",
      "style_convention": "Conventional Commits (feat, fix, docs, style, refactor, perf, test, chore, ci)"
    }
  },
  "deployment_and_installation_runbook": {
    "installation_steps": [
      "mkdir -p ~/.local/bin",
      "cp hatch.py ~/.local/bin/hatch.py",
      "chmod +x ~/.local/bin/hatch.py",
      "grep -q 'alias hatch=' ~/.zshrc || echo \"alias hatch='python3 ~/.local/bin/hatch.py'\" >> ~/.zshrc",
      "source ~/.zshrc"
    ],
    "configuration_step": "hatch --setup-global",
    "verification_steps": [
      {
        "command": "hatch --help",
        "expected_output": "Usage help output detailing templates and configuration options."
      },
      {
        "command": "git config --global --get init.templateDir",
        "expected_output": "/home/{username}/.git-templates"
      }
    ]
  },
  "troubleshooting_and_common_hurdles": [
    {
      "issue": "hatch command not found",
      "resolution": "Verify ~/.local/bin is in your PATH, or that the alias inside your active shell profile (~/.zshrc or ~/.bashrc) was loaded correctly with 'source ~/.zshrc'."
    },
    {
      "issue": "pre-commit hook failed during git commit",
      "resolution": "Address the warning (e.g. remove the secret key or fix python syntax errors) and run 'git add' on the changes before attempting to commit again. For urgent, trusted bypasses only, use 'git commit --no-verify'."
    }
  ],
  "future_roadmap_v0_3_0": {
    "planned_additions": [
      "Interactive command-line setup wizard",
      "Node.js (npm/yarn) project framework templates",
      "React Frontend SPA scaffolding structure",
      "Docker Compose environment auto-generators",
      "Terraform cloud platform template scripts"
    ]
  }
}