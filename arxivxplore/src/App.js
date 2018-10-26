import React, { Component } from 'react';
import PaperList from './components/PaperList';
import './App.css';


class App extends Component {
  constructor(props) {
    super(props);
    this.baseUrl = 'http://127.0.0.1:8000/api/papers/latest';
    this.state = {
      baseUrl: 'http://127.0.0.1:8000/api/papers/latest',
      searchResult: '',
      keywords: [],
      categories: [],
    };
  }

  updateUrl() {
    const params = [];
    if (this.state.keywords.length) params.push('keywords=' + this.state.keywords.join(','));
    if (this.state.categories.length) params.push('categories=' + this.state.categories.join(','));

    const base = [this.baseUrl];
    if (params.length) base.push(params.join('&'));
    this.setState({
      baseUrl: base.join('?'),
    });
  }

  handleSearchClick(value) {
    value.split(',').map((val) => {
      return this.state.keywords.push(val)
    })
   
    this.setState({
      searchResult: value,
    });
    this.updateUrl();
  }

  handleCategoryChange(value) {
    this.state.categories.push(value);
    this.updateUrl();
  }

  render() {
    return (
      <div id="Home">
        <Navbar keywords={this.state.keywords} handleSearchClick={this.handleSearchClick.bind(this)}/>
        <div className="App-intro container-fluid">
          <PaperList baseUrl={this.state.baseUrl} handleCategoryChange={this.handleCategoryChange.bind(this)}/>
        </div>
      </div>
    );
  }
}

class SearchBox extends Component {
  constructor(props) {
    super(props);
    this.handleSearchChange = this.handleSearchChange.bind(this);
    this.boxRef = React.createRef();
    this.state = {
      search: '',
    };
  }

  handleSearchChange (event) {
    this.setState({
      search: this.boxRef.current.value.split(' ').join(','), 
    });
    this.props.handleClick(this.boxRef.current.value.split(' ').join(','));
  }

  render () {
    return (
      <form className="navbar-form navbar-left">
      <div className="input-group">
        <input ref={this.boxRef} className="form-control" type="text" placeholder="Search.."/>
        <div className="input-group-btn">
          <button className="btn btn-default" type="button" onClick={this.handleSearchChange}>
            <img src={process.env.PUBLIC_URL+"/svg/search.svg"} width="20" height="20" alt=""/>
          </button>
        </div>
      </div>
      </form>)
  }
}

class Navbar extends Component {


  render () {
    return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light sticky-top">
    <a className="navbar-brand" href="#Home">ArXivXplorer</a>
    <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
      <span className="navbar-toggler-icon"></span>
    </button>

    <div className="collapse navbar-collapse" id="navbarSupportedContent">
    <ul className="navbar-nav mr-auto">
    <li className="nav-item active">
      <a className="nav-link" href="#Home">Home <span className="sr-only">(current)</span></a>
    </li>
    <li className="nav-item">
      <a className="nav-link" href="#About">About</a>
    </li>
    </ul>
    <form className="form-inline">
    {this.props.keywords.map( (keyword) => {
      return (
        <div className="btn-group" role="group">
          <button type="button" className="btn btn-outline-secondary btn-sm" width="20" height="20">
            <img src={process.env.PUBLIC_URL+"/svg/x.svg"} width="10" height="10" alt=""/>
          </button>
          <button type="button" className="btn btn-secondary btn-sm" disabled>{keyword}</button>
        </div>)
    })}
    </form>
    <SearchBox handleClick={this.props.handleSearchClick}/>
    </div> 
  </nav>)
  }
}


export default App;