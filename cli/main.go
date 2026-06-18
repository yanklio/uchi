package main

import (
	"context"
	"fmt"
	"os"
	"strings"

	"github.com/apenella/go-ansible/pkg/execute"
	"github.com/apenella/go-ansible/pkg/options"
	"github.com/apenella/go-ansible/pkg/playbook"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

var (
	// Gruvbox colors
	gruvRed    = lipgloss.Color("#cc241d")
	gruvGreen  = lipgloss.Color("#98971a")
	gruvYellow = lipgloss.Color("#d79921")
	gruvBlue   = lipgloss.Color("#458588")
	gruvPurple = lipgloss.Color("#b16286")
	gruvAqua   = lipgloss.Color("#689d6a")
	gruvOrange = lipgloss.Color("#d65d0e")
	gruvBg     = lipgloss.Color("#282828")
	gruvFg     = lipgloss.Color("#ebdbb2")

	titleStyle = lipgloss.NewStyle().
			Foreground(gruvPurple). // Gruvbox Purple
			Bold(true).
			MarginBottom(1)

	subtitleStyle = lipgloss.NewStyle().
			Foreground(gruvAqua). // Gruvbox Aqua
			MarginBottom(1)

	focusedStyle = lipgloss.NewStyle().Foreground(gruvYellow) // Gruvbox Yellow
	cursorStyle  = focusedStyle.Copy()
	noStyle      = lipgloss.NewStyle().Foreground(gruvFg) // Gruvbox Fg
)

const yanklioAscii = `
  __     __         _    _ _
  \ \   / /        | |  | (_)
   \ \_/ /_ _ _ __ | | _| |_  ___
    \   / _` + "`" + ` | '_ \| |/ / | |/ _ \
     | | (_| | | | |   <| | | (_) |
     |_|\__,_|_| |_|_|\_\_|_|\___/
          ~ ヤンクリオ ~
`

type sessionState int

const (
	mainMenu sessionState = iota
	setupView
	controlView
	execView
	executingAnsible
)

type executionMode string

const (
	modeSetup   executionMode = "setup"
	modeControl executionMode = "control"
	modeExec    executionMode = "exec"
)

type model struct {
	state   sessionState
	choices []string
	cursor  int

	// Setup Inputs
	setupDevice textinput.Model
	setupTags   textinput.Model

	// Control Inputs
	controlAction textinput.Model
	controlApp    textinput.Model
	controlDevice textinput.Model
	controlCursor int

	// Exec Inputs
	execRole   textinput.Model
	execDevice textinput.Model
	execCursor int

	// Focus state for forms
	focusIndex int

	// Results for execution
	executionMode executionMode
}

func initialModel() model {
	sd := textinput.New()
	sd.Placeholder = "Device limit (e.g. localhost or all)"
	sd.Focus()
	sd.PromptStyle = focusedStyle
	sd.TextStyle = focusedStyle

	st := textinput.New()
	st.Placeholder = "Tags (comma separated, e.g. server,node)"
	st.PromptStyle = noStyle
	st.TextStyle = noStyle

	ca := textinput.New()
	ca.Placeholder = "Action (up, down, restart, status)"
	ca.Focus()
	ca.PromptStyle = focusedStyle
	ca.TextStyle = focusedStyle

	capp := textinput.New()
	capp.Placeholder = "App Name (e.g. glance)"
	capp.PromptStyle = noStyle
	capp.TextStyle = noStyle

	cd := textinput.New()
	cd.Placeholder = "Device limit"
	cd.PromptStyle = noStyle
	cd.TextStyle = noStyle

	er := textinput.New()
	er.Placeholder = "Role/Tags (e.g. node,docker)"
	er.Focus()
	er.PromptStyle = focusedStyle
	er.TextStyle = focusedStyle

	ed := textinput.New()
	ed.Placeholder = "Device limit"
	ed.PromptStyle = noStyle
	ed.TextStyle = noStyle

	return model{
		state:         mainMenu,
		choices:       []string{"Setup", "Control", "Exec", "Quit"},
		setupDevice:   sd,
		setupTags:     st,
		controlAction: ca,
		controlApp:    capp,
		controlDevice: cd,
		execRole:      er,
		execDevice:    ed,
	}
}

func (m model) Init() tea.Cmd {
	return textinput.Blink
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		}
	}

	switch m.state {
	case mainMenu:
		return m.updateMainMenu(msg)
	case setupView:
		return m.updateSetup(msg)
	case controlView:
		return m.updateControl(msg)
	case execView:
		return m.updateExec(msg)
	case executingAnsible:
		return m, tea.Quit
	}

	return m, nil
}

func (m model) updateMainMenu(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q":
			return m, tea.Quit
		case "up", "k":
			if m.cursor > 0 {
				m.cursor--
			}
		case "down", "j":
			if m.cursor < len(m.choices)-1 {
				m.cursor++
			}
		case "enter", " ":
			selected := m.choices[m.cursor]
			switch selected {
			case "Setup":
				m.state = setupView
				m.focusIndex = 0
			case "Control":
				m.state = controlView
				m.controlCursor = 0
			case "Exec":
				m.state = execView
				m.execCursor = 0
			case "Quit":
				return m, tea.Quit
			}
		}
	}
	return m, nil
}

func (m model) updateSetup(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "esc":
			m.state = mainMenu
			return m, nil
		case "up", "shift+tab":
			m.focusIndex--
			if m.focusIndex < 0 {
				m.focusIndex = 2 // 2 is submit
			}
		case "down", "tab", "enter":
			if m.focusIndex == 2 && msg.String() == "enter" {
				m.state = executingAnsible
				m.executionMode = modeSetup
				return m, tea.Quit
			}
			m.focusIndex++
			if m.focusIndex > 2 {
				m.focusIndex = 0
			}
		}
	}

	if m.focusIndex == 0 {
		m.setupDevice.Focus()
		m.setupDevice.PromptStyle = focusedStyle
		m.setupDevice.TextStyle = focusedStyle
		m.setupTags.Blur()
		m.setupTags.PromptStyle = noStyle
		m.setupTags.TextStyle = noStyle
	} else if m.focusIndex == 1 {
		m.setupDevice.Blur()
		m.setupDevice.PromptStyle = noStyle
		m.setupDevice.TextStyle = noStyle
		m.setupTags.Focus()
		m.setupTags.PromptStyle = focusedStyle
		m.setupTags.TextStyle = focusedStyle
	} else {
		m.setupDevice.Blur()
		m.setupDevice.PromptStyle = noStyle
		m.setupDevice.TextStyle = noStyle
		m.setupTags.Blur()
		m.setupTags.PromptStyle = noStyle
		m.setupTags.TextStyle = noStyle
	}

	var cmd1, cmd2 tea.Cmd
	m.setupDevice, cmd1 = m.setupDevice.Update(msg)
	m.setupTags, cmd2 = m.setupTags.Update(msg)

	return m, tea.Batch(cmd1, cmd2)
}

func (m model) updateControl(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "esc":
			m.state = mainMenu
			return m, nil
		case "up", "shift+tab":
			m.controlCursor--
			if m.controlCursor < 0 {
				m.controlCursor = 3 // submit
			}
		case "down", "tab", "enter":
			if m.controlCursor == 3 && msg.String() == "enter" {
				m.state = executingAnsible
				m.executionMode = modeControl
				return m, tea.Quit
			}
			m.controlCursor++
			if m.controlCursor > 3 {
				m.controlCursor = 0
			}
		}
	}

	m.controlAction.Blur()
	m.controlAction.PromptStyle = noStyle
	m.controlAction.TextStyle = noStyle
	m.controlApp.Blur()
	m.controlApp.PromptStyle = noStyle
	m.controlApp.TextStyle = noStyle
	m.controlDevice.Blur()
	m.controlDevice.PromptStyle = noStyle
	m.controlDevice.TextStyle = noStyle

	if m.controlCursor == 0 {
		m.controlAction.Focus()
		m.controlAction.PromptStyle = focusedStyle
		m.controlAction.TextStyle = focusedStyle
	} else if m.controlCursor == 1 {
		m.controlApp.Focus()
		m.controlApp.PromptStyle = focusedStyle
		m.controlApp.TextStyle = focusedStyle
	} else if m.controlCursor == 2 {
		m.controlDevice.Focus()
		m.controlDevice.PromptStyle = focusedStyle
		m.controlDevice.TextStyle = focusedStyle
	}

	var cmd1, cmd2, cmd3 tea.Cmd
	m.controlAction, cmd1 = m.controlAction.Update(msg)
	m.controlApp, cmd2 = m.controlApp.Update(msg)
	m.controlDevice, cmd3 = m.controlDevice.Update(msg)

	return m, tea.Batch(cmd1, cmd2, cmd3)
}

func (m model) updateExec(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "esc":
			m.state = mainMenu
			return m, nil
		case "up", "shift+tab":
			m.execCursor--
			if m.execCursor < 0 {
				m.execCursor = 2 // submit
			}
		case "down", "tab", "enter":
			if m.execCursor == 2 && msg.String() == "enter" {
				m.state = executingAnsible
				m.executionMode = modeExec
				return m, tea.Quit
			}
			m.execCursor++
			if m.execCursor > 2 {
				m.execCursor = 0
			}
		}
	}

	m.execRole.Blur()
	m.execRole.PromptStyle = noStyle
	m.execRole.TextStyle = noStyle
	m.execDevice.Blur()
	m.execDevice.PromptStyle = noStyle
	m.execDevice.TextStyle = noStyle

	if m.execCursor == 0 {
		m.execRole.Focus()
		m.execRole.PromptStyle = focusedStyle
		m.execRole.TextStyle = focusedStyle
	} else if m.execCursor == 1 {
		m.execDevice.Focus()
		m.execDevice.PromptStyle = focusedStyle
		m.execDevice.TextStyle = focusedStyle
	}

	var cmd1, cmd2 tea.Cmd
	m.execRole, cmd1 = m.execRole.Update(msg)
	m.execDevice, cmd2 = m.execDevice.Update(msg)

	return m, tea.Batch(cmd1, cmd2)
}

func (m model) View() string {
	var s strings.Builder

	s.WriteString(titleStyle.Render(yanklioAscii))
	s.WriteString(subtitleStyle.Render("Homelab Configuration CLI"))
	s.WriteString("\n\n")

	switch m.state {
	case mainMenu:
		s.WriteString(lipgloss.NewStyle().Foreground(gruvFg).Render("What would you like to do?"))
		s.WriteString("\n\n")
		for i, choice := range m.choices {
			cursor := "  "
			if m.cursor == i {
				cursor = "> "
			}

			style := noStyle
			if m.cursor == i {
				style = focusedStyle
			}
			s.WriteString(style.Render(fmt.Sprintf("%s%s\n", cursor, choice)))
		}
		s.WriteString(lipgloss.NewStyle().Foreground(gruvOrange).Render("\nPress q to quit.\n"))

	case setupView:
		s.WriteString(lipgloss.NewStyle().Foreground(gruvGreen).Bold(true).Render("--- Setup Playbook ---"))
		s.WriteString("\nRuns playbooks/site.yml\n\n")

		s.WriteString(m.setupDevice.View() + "\n")
		s.WriteString(m.setupTags.View() + "\n\n")

		button := "[ Submit ]"
		if m.focusIndex == 2 {
			button = focusedStyle.Render("[ Submit ]")
		} else {
			button = noStyle.Render("[ Submit ]")
		}
		s.WriteString(button + "\n\n")
		s.WriteString(lipgloss.NewStyle().Foreground(gruvOrange).Render("Press Esc to go back.\n"))

	case controlView:
		s.WriteString(lipgloss.NewStyle().Foreground(gruvBlue).Bold(true).Render("--- Control Playbook ---"))
		s.WriteString("\nRuns playbooks/control.yml\n\n")

		s.WriteString(m.controlAction.View() + "\n")
		s.WriteString(m.controlApp.View() + "\n")
		s.WriteString(m.controlDevice.View() + "\n\n")

		button := "[ Submit ]"
		if m.controlCursor == 3 {
			button = focusedStyle.Render("[ Submit ]")
		} else {
			button = noStyle.Render("[ Submit ]")
		}
		s.WriteString(button + "\n\n")
		s.WriteString(lipgloss.NewStyle().Foreground(gruvOrange).Render("Press Esc to go back.\n"))

	case execView:
		s.WriteString(lipgloss.NewStyle().Foreground(gruvRed).Bold(true).Render("--- Exec Playbook ---"))
		s.WriteString("\nRuns playbooks/roles.yml\n\n")

		s.WriteString(m.execRole.View() + "\n")
		s.WriteString(m.execDevice.View() + "\n\n")

		button := "[ Submit ]"
		if m.execCursor == 2 {
			button = focusedStyle.Render("[ Submit ]")
		} else {
			button = noStyle.Render("[ Submit ]")
		}
		s.WriteString(button + "\n\n")
		s.WriteString(lipgloss.NewStyle().Foreground(gruvOrange).Render("Press Esc to go back.\n"))

	case executingAnsible:
		s.WriteString(lipgloss.NewStyle().Foreground(gruvYellow).Render("Preparing to execute Ansible...\n"))
	}

	return s.String()
}

func runAnsible(m model) error {
	var playbookFile string
	ansiblePlaybookConnectionOptions := &options.AnsibleConnectionOptions{}
	ansiblePlaybookOptions := &playbook.AnsiblePlaybookOptions{
		Inventory: "../inventory.yaml",
	}

	switch m.executionMode {
	case modeSetup:
		playbookFile = "../playbooks/site.yml"

		if limit := m.setupDevice.Value(); limit != "" {
			ansiblePlaybookOptions.Limit = limit
		}
		if tags := m.setupTags.Value(); tags != "" {
			ansiblePlaybookOptions.Tags = tags
		}

	case modeControl:
		playbookFile = "../playbooks/control.yml"

		if limit := m.controlDevice.Value(); limit != "" {
			ansiblePlaybookOptions.Limit = limit
		}

		vars := map[string]interface{}{}
		if action := m.controlAction.Value(); action != "" {
			vars["control_action"] = action
		}
		if app := m.controlApp.Value(); app != "" {
			vars["control_app"] = app
		}

		if len(vars) > 0 {
			for k, v := range vars {
				ansiblePlaybookOptions.AddExtraVar(k, v)
			}
		}

	case modeExec:
		playbookFile = "../playbooks/roles.yml"

		if limit := m.execDevice.Value(); limit != "" {
			ansiblePlaybookOptions.Limit = limit
		}
		if tags := m.execRole.Value(); tags != "" {
			ansiblePlaybookOptions.Tags = tags
		}
	default:
		return nil // No execution
	}

	fmt.Printf("\nExecuting Playbook: %s\n", playbookFile)

	exe := execute.NewDefaultExecute(
		execute.WithWrite(os.Stdout),
	)

	pbCmd := &playbook.AnsiblePlaybookCmd{
		Playbooks:         []string{playbookFile},
		ConnectionOptions: ansiblePlaybookConnectionOptions,
		Options:           ansiblePlaybookOptions,
		Exec:              exe,
	}

	err := pbCmd.Run(context.TODO())
	if err != nil {
		return fmt.Errorf("error running playbook: %w", err)
	}

	return nil
}

func main() {
	p := tea.NewProgram(initialModel())
	finalModel, err := p.Run()
	if err != nil {
		fmt.Printf("Alas, there's been an error: %v", err)
		os.Exit(1)
	}

	m := finalModel.(model)
	if m.state == executingAnsible {
		err := runAnsible(m)
		if err != nil {
			fmt.Printf("Ansible execution failed: %v\n", err)
			os.Exit(1)
		}
	}
}
