import React, { Component } from 'react';
import PaperInList from './PaperInList';

function throttle(fn, threshhold, scope) {
  threshhold || (threshhold = 250);
  var last,
      deferTimer;
  return function () {
    var context = scope || this;

    var now = +new Date(),
        args = arguments;
    if (last && now < last + threshhold) {
      // hold on to it
      clearTimeout(deferTimer);
      deferTimer = setTimeout(function () {
        last = now;
        fn.apply(context, args);
      }, threshhold);
    } else {
      last = now;
      fn.apply(context, args);
    }
  };
}

class PaperList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      content: [], 
      loading: true
    };
    this.onScrollListener = this.onScrollListener.bind(this);
    this.throttledOnScrollListener = throttle(this.onScrollListener, 250).bind(this);
  }
  
  isElementAtBottom (target, scrollThreshold = 0.98) {
    const clientHeight = (target === document.body || target === document.documentElement)
    ? window.screen.availHeight : target.clientHeight;

    return (target.scrollTop + clientHeight) >= scrollThreshold * target.scrollHeight;
  }

  onScrollListener (event) {
    let target = this.props.height || this.props.scrollableTarget
      ? event.target
      : (document.documentElement.scrollTop ? document.documentElement : document.body);
    
    let atBottom = this.isElementAtBottom(target);

    if (atBottom && this.state.more && !this.state.loadingMore) {
      this.setState({loadingMore: true});
      fetch(this.state.more).then((res) => res.json())
        .then((data) => {
          if (data.results) this.setState({
            content: this.state.content.concat(data.results), 
            loadingMore: false, 
            more: data.next
          })
        });
    }
  }

  componentWillReceiveProps(nextProps){
    
    if(nextProps.baseUrl !== this.props.baseUrl){
        this.setState({
          content: [], 
          loading: true
        });

        fetch(nextProps.baseUrl)
          .then((res) => res.json())
          .then((data) => {
            if (data.results) this.setState({
              content: data.results, 
              loading: false, 
              more: data.next
            })
          })
    }
  }

  componentWillUnmount() {
    window.removeEventListener('scroll', this.throttledOnScrollListener);
  }

  componentDidMount () {
    window.addEventListener('scroll', this.throttledOnScrollListener);
    fetch(this.props.baseUrl)
      .then((res) => res.json())
      .then((data) => {
        if (data.results) this.setState({content: data.results, loading: false, more: data.next})})
  }

  render() {  

    let loading = (
    <div><div className="spinner">
      <div className="bounce1"></div>
      <div className="bounce2"></div>
      <div className="bounce3"></div>
    </div></div>);

    const listItems = this.state.content.length ? 
      this.state.content.map((paper, index) => {
        paper.collapsed = true;
        return (
          <div className="row box" key={index.toString()}>
            <PaperInList state={paper} key={index.toString()} ident={index.toString()}/>
          </div>
        )
      }) : 
      "Sorry, no results";
    return (
        <div className="wrapper container">
          {this.state.loading ? loading: listItems}
          {this.state.loadingMore && !this.state.loading ? loading : null}
        </div>
    )
  }
}

export default PaperList;