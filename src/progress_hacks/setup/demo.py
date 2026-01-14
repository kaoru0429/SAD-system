#!/usr/bin/env python
"""
Demo Script - 五言絕句設定流程示範

Interactive demo of the Five Hacks setup wizard.
五言絕句設定精靈的互動式示範。

Usage:
    python -m src.progress_hacks.setup.demo
"""

from pathlib import Path
import tempfile

from .wizard import SetupWizard


def main() -> None:
    """Run interactive demo."""
    print("\n" + "=" * 60)
    print("  Five Hacks Setup Demo | 五言絕句設定示範")
    print("=" * 60 + "\n")
    
    # Use temp directory for demo
    with tempfile.TemporaryDirectory() as tmpdir:
        wizard = SetupWizard(config_path=Path(tmpdir) / "config.json")
        
        # Show welcome
        print(wizard.get_welcome_message())
        
        # Interactive loop
        complete = False
        while not complete:
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ("q", "quit", "exit"):
                print("\n👋 Demo cancelled | 示範已取消")
                return
            
            response, complete = wizard.process_input(user_input)
            print(response)
        
        # Show final config
        print("\n" + "=" * 60)
        print("  Final Configuration | 最終配置")
        print("=" * 60)
        print(f"\n  Enabled hacks: {wizard.config.enabled_hacks}")
        print(f"  Preset used: {wizard.config.preset_used}")
        print(f"  Config saved to: {wizard._config_path}")
        print()


def demo_all_screens() -> None:
    """Show all screens without interaction."""
    with tempfile.TemporaryDirectory() as tmpdir:
        wizard = SetupWizard(config_path=Path(tmpdir) / "config.json")
        
        print("\n" + "=" * 60)
        print("  Screen 1: Welcome")
        print("=" * 60)
        print(wizard.get_welcome_message())
        
        print("\n" + "=" * 60)
        print("  Screen 2: Preset Menu")
        print("=" * 60)
        print(wizard.get_preset_menu())
        
        print("\n" + "=" * 60)
        print("  Screen 3: Custom Menu")
        print("=" * 60)
        wizard._config.enabled_hacks = ["clarify", "self_grade", "devils_advocate"]
        print(wizard.get_custom_menu())
        
        print("\n" + "=" * 60)
        print("  Screen 4: Completion")
        print("=" * 60)
        response, _ = wizard.apply_preset("recommended")
        print(response)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        demo_all_screens()
    else:
        main()
