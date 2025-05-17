"""
Helper module for managing menu icons using QtAwesome.

This module keeps the icon definitions separate from the controller logic,
making the code more maintainable and easier to update.
"""

import qtawesome as qta

def apply_icons(window):
    """
    Apply QtAwesome icons to all menu actions in the main window.
    
    Args:
        window: The main window object with menu actions
    """
    # Apply icons to File menu actions
    _apply_file_menu_icons(window)
    
    # Apply icons to Edit menu actions
    _apply_edit_menu_icons(window)
    
    # Apply icons to View menu actions
    _apply_view_menu_icons(window)
    
    # Apply icons to Settings menu actions
    _apply_settings_menu_icons(window)
    
    # Apply icons to Prompt menu actions
    _apply_prompt_menu_icons(window)
    
    # Apply icons to Help menu actions
    _apply_help_menu_icons(window)

def _apply_file_menu_icons(window):
    """Apply icons to File menu actions."""
    window.actionNew.setIcon(qta.icon('fa6s.file'))
    window.actionOpen_Image.setIcon(qta.icon('fa6s.image'))
    window.actionOpen_Multiple_Images.setIcon(qta.icon('fa6s.images'))
    window.actionOpen_Folder.setIcon(qta.icon('fa6s.folder-open'))
    window.actionOpen_Multiple_Folders.setIcon(qta.icon('fa6s.folder-tree'))
    window.actionOpen_Video.setIcon(qta.icon('fa6s.video'))
    window.actionOpen_Multiple_Videos.setIcon(qta.icon('fa6s.film'))
    window.actionQuit.setIcon(qta.icon('fa6s.right-from-bracket'))
    
    # Export actions
    window.actionExport_CSV_Freepik.setIcon(qta.icon('fa6s.file-export'))
    window.actionExport_CSV_Shutterstock.setIcon(qta.icon('fa6s.file-export'))
    window.actionExport_CSV_Adobe_Stock.setIcon(qta.icon('fa6s.file-export'))
    window.actionExport_CSV_iStock.setIcon(qta.icon('fa6s.file-export'))

def _apply_edit_menu_icons(window):
    """Apply icons to Edit menu actions."""
    window.actionCut.setIcon(qta.icon('fa6s.scissors'))
    window.actionCopy.setIcon(qta.icon('fa6s.copy'))
    window.actionPaste.setIcon(qta.icon('fa6s.paste'))
    window.actionDelete.setIcon(qta.icon('fa6s.trash'))
    window.actionSelect_All.setIcon(qta.icon('fa6s.check-double'))
    window.actionDeselect_All.setIcon(qta.icon('fa6s.xmark'))
    window.actionRefresh.setIcon(qta.icon('fa6s.arrows-rotate'))
    window.actionClear.setIcon(qta.icon('fa6s.broom'))
    window.actionRename.setIcon(qta.icon('fa6s.pen-to-square'))
    window.actionRename_All.setIcon(qta.icon('fa6s.pen-clip'))

def _apply_view_menu_icons(window):
    """Apply icons to View menu actions."""
    # Appearance actions
    window.actionFull_Screen.setIcon(qta.icon('fa6s.expand'))
    window.actionWindowed.setIcon(qta.icon('fa6s.compress'))
    window.actionCenter.setIcon(qta.icon('fa6s.arrows-to-dot'))
    
    # Layout actions
    window.actionDefault.setIcon(qta.icon('fa6s.table-columns'))
    window.actionBatch_Processing.setIcon(qta.icon('fa6s.layer-group'))
    window.actionMetadata_Editing.setIcon(qta.icon('fa6s.pen-to-square'))
    window.actionMetadata_Analysis.setIcon(qta.icon('fa6s.chart-simple'))

def _apply_settings_menu_icons(window):
    """Apply icons to Settings menu actions."""
    window.actionPreferences.setIcon(qta.icon('fa6s.gear'))
    window.actionGoogle_Gemini.setIcon(qta.icon('fa6s.star'))
    window.actionOpen_AI.setIcon(qta.icon('fa6s.brain'))

def _apply_prompt_menu_icons(window):
    """Apply icons to Prompt menu actions."""
    window.actionDefault_Prompt.setIcon(qta.icon('fa6s.sliders'))
    window.actionCustom_Prompt.setIcon(qta.icon('fa6s.pen-fancy'))
    window.actionNegative_Prompt.setIcon(qta.icon('fa6s.ban'))
    window.actionMetadata_Prompt_2.setIcon(qta.icon('fa6s.tags'))
    window.actionPrompt_Preferences.setIcon(qta.icon('fa6s.puzzle-piece'))

def _apply_help_menu_icons(window):
    """Apply icons to Help menu actions."""
    window.actionWhatsApp_Group.setIcon(qta.icon('fa6b.whatsapp'))
    window.actionLicense.setIcon(qta.icon('fa6s.certificate'))
    window.actionContributors.setIcon(qta.icon('fa6s.users'))
    window.actionReport_Issue.setIcon(qta.icon('fa6s.bug'))
    window.actionGithub_Repository.setIcon(qta.icon('fa6b.github'))
    window.actionCheck_for_Updates.setIcon(qta.icon('fa6s.download'))
    window.actionDonate.setIcon(qta.icon('fa6s.heart', color='#ff1764'))
    window.actionAbout_2.setIcon(qta.icon('fa6s.circle-info'))
