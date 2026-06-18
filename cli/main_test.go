package main

import (
	"testing"
)

func TestInitialModel(t *testing.T) {
	m := initialModel()
	if m.state != mainMenu {
		t.Errorf("expected initial state to be mainMenu, got %v", m.state)
	}
	if len(m.choices) != 4 {
		t.Errorf("expected 4 choices, got %d", len(m.choices))
	}
}
