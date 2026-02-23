// Professional UI Shell
import React, { useState } from 'react';
import { 
  Container, AppBar, Toolbar, Typography, Box, Drawer, List, ListItem,
  ListItemIcon, ListItemText, IconButton, Badge, Avatar, Paper, Grid,
  Card, CardContent, Button, TextField
} from '@mui/material';
import {
  Menu as MenuIcon, Dashboard as DashboardIcon, People as PeopleIcon,
  Settings as SettingsIcon, Notifications as NotificationsIcon,
  Person as PersonIcon
} from '@mui/icons-material';
import { createTheme, ThemeProvider } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: { main: '#2563eb' },
    secondary: { main: '#7c3aed' },
    background: { default: '#f3f4f6' }
  }
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display: 'flex' }}>
        <AppBar position="fixed">
          <Toolbar>
            <Typography variant="h6" sx={{ flexGrow: 1 }}>
              Pharmacy Manager
            </Typography>
            <IconButton color="inherit">
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            <IconButton color="inherit">
              <Avatar><PersonIcon /></Avatar>
            </IconButton>
          </Toolbar>
        </AppBar>
        <Drawer variant="permanent" sx={{ width: 240 }}>
          <Toolbar />
          <List>
            <ListItem button><ListItemIcon><DashboardIcon /></ListItemIcon><ListItemText primary="Dashboard" /></ListItem>
            <ListItem button><ListItemIcon><PeopleIcon /></ListItemIcon><ListItemText primary="Users" /></ListItem>
            <ListItem button><ListItemIcon><SettingsIcon /></ListItemIcon><ListItemText primary="Settings" /></ListItem>
          </List>
        </Drawer>
        <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
          <Toolbar />
          <Container>
            <Typography variant="h4">Welcome to Your App</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6">Dashboard</Typography>
                    <Typography>Your content here</Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;