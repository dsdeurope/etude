import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null, info: null };
  }
  static getDerivedStateFromError(error) {
    return { error };
  }
  componentDidCatch(error, info) {
    this.setState({ info });
    console.error('ErrorBoundary', error, info);
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 20, fontFamily: 'monospace' }}>
          <h2>💥 Runtime error</h2>
          <pre>{String(this.state.error && this.state.error.message)}</pre>
          {this.state.error?.stack && (
            <>
              <h3>Stack</h3>
              <pre>{this.state.error.stack}</pre>
            </>
          )}
          {this.state.info?.componentStack && (
            <>
              <h3>Component stack</h3>
              <pre>{this.state.info.componentStack}</pre>
            </>
          )}
        </div>
      );
    }
    return this.props.children;
  }
}
