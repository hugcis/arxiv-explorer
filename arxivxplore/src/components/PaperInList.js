import React, { Component } from 'react';

export class PaperInList extends Component {
  constructor(props) {
    super(props);
    this.state = props.state;
  }

  componentDidMount() {
    const MathJax = window.MathJax;
    MathJax.Hub.Queue(
      ["Typeset", MathJax.Hub]
    );
  }

  renderPaperModal(key) {
    return <ModalPaper state={this.state} ident={key}/>
  }
  
  render() {
    return (
      <div className="container-fluid">
        <div className="row-pl-5">
          <a href={'https://arxiv.org/abs/'+this.state.doi}  target="_blank">{this.state.title}</a>
        </div>
        <div className="row-pl-5">
          {this.state.authors.map((author) => {
            return (author.forenames ? author.forenames + ' ' : '') + 
              (author.keyname) + 
              (author.affiliation ? ' (' +author.affiliation + ')' : '')
          }).join(' - ')}
        </div>
        <div className="row-pl-5 categories">
          {this.state.categories.join(' ')}
        </div>
        <div className="row">
          <div className="col">
              {"DOI: "} <a href={'https://arxiv.org/abs/'+this.state.doi}  target="_blank">{this.state.doi}</a>
          </div>
          <div className="col">{"Date: " + this.state.date}</div>
        </div>
        <div className="mathjax">
          {this.state.abstract.length>800? this.state.abstract.slice(0, 800) + '...': this.state.abstract}     
        </div>
        {this.renderPaperModal(this.props.ident)}
      </div>)
    }
}
  
class ModalPaper extends Component {
  constructor(props) {
    super(props);
    this.state = props.state;
  }

  render() {
    return (
      <div>
      <button type="button" className="btn btn-sm btn-info" data-toggle="modal" data-target={"#myModal"+this.props.ident}>
        Read More
      </button>

        <div className="modal fade" id={"myModal"+this.props.ident} tabIndex="-1" role="dialog" aria-labelledby="myLargeModalLabel" aria-hidden="true">
          <div className="modal-dialog modal-lg" role="document">
            <div className="modal-content">
              <div className="modal-header">
                <a href={'https://arxiv.org/abs/'+this.state.doi}  target="_blank"><h5 className="modal-title">{this.state.title}</h5></a>
              </div>
              <div className="modal-header">
                {this.state.categories.join(' ')}
              </div>
              <div className="modal-body">
                <p className="mathjax">{this.state.abstract}</p>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-default" data-dismiss="modal">Close</button>
              </div>
            </div>
          </div>
        </div></div>)
  }
}

export default PaperInList;